import re

from typing import Type

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.chat.telegram import MessageEvent, CommandMessageEvent, TextMessageEvent, \
    PhotoMessageEvent, VideoMessageEvent, ContactMessageEvent, DocumentMessageEvent
from platypush.plugins.chat.telegram import ChatTelegramPlugin


class ChatTelegramBackend(Backend):
    """
    Telegram bot that listens for messages and updates.

    Triggers:

        * :class:`platypush.message.event.chat.telegram.TextMessageEvent` when a text message is received.
        * :class:`platypush.message.event.chat.telegram.PhotoMessageEvent` when a photo is received.
        * :class:`platypush.message.event.chat.telegram.VideoMessageEvent` when a video is received.
        * :class:`platypush.message.event.chat.telegram.ContactMessageEvent` when a contact is received.
        * :class:`platypush.message.event.chat.telegram.DocumentMessageEvent` when a document is received.
        * :class:`platypush.message.event.chat.telegram.CommandMessageEvent` when a command message is received.

    Requires:

        * The :class:`platypush.plugins.chat.telegram.ChatTelegramPlugin` plugin configured

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._plugin: ChatTelegramPlugin = get_plugin('chat.telegram')

    def _msg_hook(self, cls: Type[MessageEvent]):
        # noinspection PyUnusedLocal
        def hook(update, context):
            self.bus.post(cls(chat_id=update.effective_chat.id,
                              message=self._plugin.parse_msg(update.effective_message).output,
                              user=self._plugin.parse_user(update.effective_user).output))

        return hook

    def _command_hook(self):
        # noinspection PyUnusedLocal
        def hook(update, context):
            msg = update.effective_message
            m = re.match('\s*/([0-9a-zA-Z]+)\s*(.*)', msg.text)
            cmd = m.group(1).lower()
            args = [arg for arg in re.split('\s+', m.group(2)) if len(arg)]
            self.bus.post(CommandMessageEvent(chat_id=update.effective_chat.id,
                                              command=cmd,
                                              cmdargs=args,
                                              message=self._plugin.parse_msg(msg).output,
                                              user=self._plugin.parse_user(update.effective_user).output))

        return hook

    def run(self):
        # noinspection PyPackageRequirements
        from telegram.ext import MessageHandler, Filters

        super().run()
        telegram = self._plugin.get_telegram()
        dispatcher = telegram.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.text, self._msg_hook(TextMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.photo, self._msg_hook(PhotoMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.video, self._msg_hook(VideoMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.location, self._msg_hook(ContactMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.document, self._msg_hook(DocumentMessageEvent)))
        dispatcher.add_handler(MessageHandler(Filters.command, self._command_hook()))

        self.logger.info('Initialized Telegram backend')
        telegram.start_polling()


# vim:sw=4:ts=4:et:
