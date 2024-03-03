import asyncio as aio
import logging
import os
import re

from multiprocessing import Event, Process, Queue
from typing import Callable, Coroutine, Optional, Set, Type, Union

from telegram import Message, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

from platypush.context import get_bus
from platypush.message.event.telegram import (
    MessageEvent,
    CommandMessageEvent,
    TextMessageEvent,
    PhotoMessageEvent,
    VideoMessageEvent,
    ContactMessageEvent,
    DocumentMessageEvent,
    LocationMessageEvent,
    GroupChatCreatedEvent,
)

from ._bridge import CommandBridge
from ._model import END_OF_SERVICE, Resource
from ._utils import dump_msg, dump_user


class TelegramService(Process):
    """
    Background service to handle Telegram messages and events.
    """

    def __init__(
        self,
        api_token: str,
        cmd_queue: Queue,
        result_queue: Queue,
        authorized_chat_ids: Set[Union[str, int]],
        *_,
        **__,
    ):
        super().__init__(name="telegram-service")
        self.logger = logging.getLogger("platypush:telegram")
        self.authorized_chat_ids = set(authorized_chat_ids or [])
        self._cmd_queue = cmd_queue
        self._result_queue = result_queue
        self._loop = aio.new_event_loop()
        self._app = self._build_app(api_token)
        self._service_running = Event()
        self._service_stopped = Event()
        self._cmd_bridge = CommandBridge(self)

    def _build_app(self, api_token: str) -> Application:
        app = ApplicationBuilder().token(api_token).build()
        app.add_handler(MessageHandler(filters.ChatType.GROUPS, self._group_hook()))

        app.add_handler(
            MessageHandler(
                filters.TEXT & (~filters.COMMAND), self._msg_hook(TextMessageEvent)
            )
        )

        app.add_handler(
            MessageHandler(filters.PHOTO, self._msg_hook(PhotoMessageEvent))
        )

        app.add_handler(
            MessageHandler(filters.VIDEO, self._msg_hook(VideoMessageEvent))
        )

        app.add_handler(
            MessageHandler(filters.CONTACT, self._msg_hook(ContactMessageEvent))
        )

        app.add_handler(
            MessageHandler(filters.LOCATION, self._msg_hook(LocationMessageEvent))
        )

        app.add_handler(
            MessageHandler(filters.Document.ALL, self._msg_hook(DocumentMessageEvent))
        )

        app.add_handler(MessageHandler(filters.COMMAND, self._command_hook()))
        return app

    async def _authorize(self, msg: Message, context: ContextTypes.DEFAULT_TYPE):
        if not self.authorized_chat_ids:
            return

        if msg.chat.type == 'private' and msg.chat.id not in self.authorized_chat_ids:
            self.logger.info(
                'Received message from unauthorized chat_id %s', msg.chat.id
            )

            await context.bot.send_message(
                chat_id=msg.chat.id,
                text='You are not allowed to send messages to this bot',
            )

            raise PermissionError

    def _msg_hook(self, cls: Type[MessageEvent]):
        async def hook(update: Update, context: ContextTypes.DEFAULT_TYPE):
            msg = update.effective_message
            if not msg:
                return

            try:
                await self._authorize(msg, context)
                self.bus.post(
                    cls(
                        chat_id=(
                            update.effective_chat.id if update.effective_chat else None
                        ),
                        message=dump_msg(msg) if msg else None,
                        user=(
                            dump_user(update.effective_user)
                            if update.effective_user
                            else None
                        ),
                    )
                )
            except PermissionError:
                pass

        return hook

    def _group_hook(self):
        async def hook(update: Update, context):
            msg = update.effective_message
            if not msg:
                return

            if msg.group_chat_created:
                self.bus.post(
                    GroupChatCreatedEvent(
                        chat_id=(
                            update.effective_chat.id if update.effective_chat else None
                        ),
                        message=dump_msg(msg),
                        user=(
                            dump_user(update.effective_user)
                            if update.effective_user
                            else None
                        ),
                    )
                )
            elif msg.photo:
                await self._msg_hook(PhotoMessageEvent)(update, context)
            elif msg.video:
                await self._msg_hook(VideoMessageEvent)(update, context)
            elif msg.contact:
                await self._msg_hook(ContactMessageEvent)(update, context)
            elif msg.location:
                await self._msg_hook(LocationMessageEvent)(update, context)
            elif msg.document:
                await self._msg_hook(DocumentMessageEvent)(update, context)
            elif msg.text:
                if msg.text.startswith('/'):
                    await self._command_hook()(update, context)
                else:
                    await self._msg_hook(TextMessageEvent)(update, context)

        return hook

    def _command_hook(self):
        async def hook(update: Update, context: ContextTypes.DEFAULT_TYPE):
            msg = update.effective_message
            if not (msg and msg.text):
                return

            m = re.match(r'\s*/([0-9a-zA-Z_-]+)\s*(.*)', msg.text)
            if not m:
                self.logger.warning('Invalid command: %s', msg.text)
                return

            cmd = m.group(1).lower()
            args = [arg for arg in re.split(r'\s+', m.group(2)) if len(arg)]

            try:
                await self._authorize(msg, context)
                self.bus.post(
                    CommandMessageEvent(
                        chat_id=(
                            update.effective_chat.id if update.effective_chat else None
                        ),
                        command=cmd,
                        cmdargs=args,
                        message=dump_msg(msg),
                        user=(
                            dump_user(update.effective_user)
                            if update.effective_user
                            else None
                        ),
                    )
                )
            except PermissionError:
                pass

        return hook

    def _exec(
        self,
        method: Callable[..., Coroutine],
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        fut = aio.run_coroutine_threadsafe(method(*args, **kwargs), self._loop)
        return fut.result(timeout=timeout)

    def exec(
        self,
        cmd: str,
        *args,
        timeout: Optional[float] = None,
        resource: Optional[Resource] = None,
        resource_attr: Optional[str] = None,
        **kwargs,
    ):
        method = getattr(self._app.bot, cmd, None)
        assert method, f"Method {cmd} not found"

        if resource:
            assert resource_attr, f"Resource attribute not specified for command {cmd}"
            with resource as file:
                kwargs[resource_attr] = file
                return self._exec(
                    method,
                    *args,
                    timeout=timeout,
                    **kwargs,
                )

        return self._exec(method, *args, timeout=timeout, **kwargs)

    def _run(self):
        self._app.run_polling()

    def run(self):
        super().run()
        self._service_running.set()
        self._service_stopped.clear()
        aio.set_event_loop(self._loop)
        self._cmd_bridge.start()

        try:
            self._run()
        except Exception as e:
            self.logger.error("Telegram polling error: %s", e, exc_info=True)
        finally:
            self._service_running.clear()
            self._service_stopped.set()
            self._cmd_queue.put_nowait(END_OF_SERVICE)

    def stop(self):
        self._cmd_queue.put_nowait(END_OF_SERVICE)
        self._app.stop_running()

        if self.is_alive() and self.pid != os.getpid():
            self.terminate()
            self.join(timeout=5)

            if self.is_alive():
                self.kill()

    @property
    def bus(self):
        return get_bus()

    @property
    def cmd_queue(self):
        return self._cmd_queue

    @property
    def result_queue(self):
        return self._result_queue

    @property
    def stop_event(self):
        return self._service_stopped

    def is_running(self):
        return self._service_running.is_set()

    @property
    def run_event(self):
        return self._service_running


# vim:sw=4:ts=4:et:
