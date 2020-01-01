import re

from typing import Type, Optional, Union, List

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.chat.telegram import MessageEvent, CommandMessageEvent, TextMessageEvent, \
    PhotoMessageEvent, VideoMessageEvent, ContactMessageEvent, DocumentMessageEvent, LocationMessageEvent, \
    GroupChatCreatedEvent
from platypush.plugins.chat.telegram import ChatTelegramPlugin


class ChatTelegramBackend(Backend):
    """
    Telegram bot that listens for messages and updates.

    Triggers:

        * :class:`platypush.message.event.chat.telegram.TextMessageEvent` when a text message is received.
        * :class:`platypush.message.event.chat.telegram.PhotoMessageEvent` when a photo is received.
        * :class:`platypush.message.event.chat.telegram.VideoMessageEvent` when a video is received.
        * :class:`platypush.message.event.chat.telegram.LocationMessageEvent` when a location is received.
        * :class:`platypush.message.event.chat.telegram.ContactMessageEvent` when a contact is received.
        * :class:`platypush.message.event.chat.telegram.DocumentMessageEvent` when a document is received.
        * :class:`platypush.message.event.chat.telegram.CommandMessageEvent` when a command message is received.
        * :class:`platypush.message.event.chat.telegram.GroupCreatedEvent` when the bot is invited to a new group.

    Requires:

        * The :class:`platypush.plugins.chat.telegram.ChatTelegramPlugin` plugin configured

    """

    def __init__(self, authorized_chat_ids: Optional[List[Union[str, int]]] = None, **kwargs):
        """
        :param authorized_chat_ids: Optional list of chat_id/user_id which are authorized to send messages to
            the bot. If nothing is specified then no restrictions are applied.
        """

        super().__init__(**kwargs)
        self.authorized_chat_ids = set(authorized_chat_ids or [])
        self._plugin: ChatTelegramPlugin = get_plugin('chat.telegram')

    def _authorize(self, msg):
        if not self.authorized_chat_ids:
            return

        if msg.chat.type == 'private' and msg.chat.id not in self.authorized_chat_ids:
            self.logger.info('Received message from unauthorized chat_id {}'.format(msg.chat.id))
            self._plugin.send_message(chat_id=msg.chat.id, text='You are not allowed to send messages to this bot')
            raise PermissionError

    def _msg_hook(self, cls: Type[MessageEvent]):
        # noinspection PyUnusedLocal
        def hook(update, context):
            msg = update.effective_message

            try:
                self._authorize(msg)
                self.bus.post(cls(chat_id=update.effective_chat.id,
                                  message=self._plugin.parse_msg(msg).output,
                                  user=self._plugin.parse_user(update.effective_user).output))
            except PermissionError:
                pass

        return hook

    def _group_hook(self):
        # noinspection PyUnusedLocal
        def hook(update, context):
            msg = update.effective_message
            if msg.group_chat_created:
                self.bus.post(GroupChatCreatedEvent(chat_id=update.effective_chat.id,
                                                    message=self._plugin.parse_msg(msg).output,
                                                    user=self._plugin.parse_user(update.effective_user).output))
            elif msg.photo:
                self._msg_hook(PhotoMessageEvent)(update, context)
            elif msg.video:
                self._msg_hook(VideoMessageEvent)(update, context)
            elif msg.contact:
                self._msg_hook(ContactMessageEvent)(update, context)
            elif msg.location:
                self._msg_hook(LocationMessageEvent)(update, context)
            elif msg.document:
                self._msg_hook(DocumentMessageEvent)(update, context)
            elif msg.text:
                if msg.text.startswith('/'):
                    self._command_hook()(update, context)
                else:
                    self._msg_hook(TextMessageEvent)(update, context)

        return hook

    def _command_hook(self):
        # noinspection PyUnusedLocal
        def hook(update, context):
            msg = update.effective_message
            m = re.match('\s*/([0-9a-zA-Z_-]+)\s*(.*)', msg.text)
            cmd = m.group(1).lower()
            args = [arg for arg in re.split('\s+', m.group(2)) if len(arg)]

            try:
                self._authorize(msg)
                self.bus.post(CommandMessageEvent(chat_id=update.effective_chat.id,
                                                  command=cmd,
                                                  cmdargs=args,
                                                  message=self._plugin.parse_msg(msg).output,
                                                  user=self._plugin.parse_user(update.effective_user).output))
            except PermissionError:
                pass

        return hook

    def run(self):
        # noinspection PyPackageRequirements
        from telegram.ext import MessageHandler, Filters

        super().run()
        telegram = self._plugin.get_telegram()
        dispatcher = telegram.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.group, self._group_hook()))
        dispatcher.add_handler(MessageHandler(Filters.text, self._msg_hook(TextMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.photo, self._msg_hook(PhotoMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.video, self._msg_hook(VideoMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.contact, self._msg_hook(ContactMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.location, self._msg_hook(LocationMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.document, self._msg_hook(DocumentMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.command, self._command_hook()))

        self.logger.info('Initialized Telegram backend')
        telegram.start_polling()


# vim:sw=4:ts=4:et:
