from typing import List, Optional

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.chat.telegram import NewMessageEvent, NewCommandMessageEvent
from platypush.plugins.chat.telegram import ChatTelegramPlugin


class ChatTelegramBackend(Backend):
    """
    Telegram bot that listens for messages and updates.

    Triggers:

        * :class:`platypush.message.event.chat.telegram.NewMessageEvent` when a new message is received.
        * :class:`platypush.message.event.chat.telegram.NewCommandMessageEvent` when a new command message is received.

    Requires:

        * The :class:`platypush.plugins.chat.telegram.ChatTelegramPlugin` plugin configured

    """

    def __init__(self, commands: Optional[List[str]] = None, **kwargs):
        """
        :param commands: Optional list of commands to be registered on the bot (e.g. 'start', 'stop', 'help' etc.).
            When you send e.g. '/start' to the bot conversation then a
            :class:`platypush.message.event.chat.telegram.NewCommandMessageEvent` will be triggered instead of a
            :class:`platypush.message.event.chat.telegram.NewMessageEvent` event.
        """
        super().__init__(**kwargs)
        self.commands = commands or []
        self._plugin: ChatTelegramPlugin = get_plugin('chat.telegram')

    def _msg_hook(self):
        # noinspection PyUnusedLocal
        def hook(update, context):
            self.bus.post(NewMessageEvent(chat_id=update.effective_chat.id,
                                          message=self._plugin.parse_msg(update.effective_message).output,
                                          user=self._plugin.parse_user(update.effective_user).output))
        return hook

    def _command_hook(self, cmd):
        # noinspection PyUnusedLocal
        def hook(update, context):
            self.bus.post(NewCommandMessageEvent(command=cmd,
                                                 chat_id=update.effective_chat.id,
                                                 message=self._plugin.parse_msg(update.effective_message).output,
                                                 user=self._plugin.parse_user(update.effective_user).output))

        return hook

    def run(self):
        # noinspection PyPackageRequirements
        from telegram.ext import CommandHandler, MessageHandler, Filters

        super().run()
        telegram = self._plugin.get_telegram()
        dispatcher = telegram.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self._msg_hook()))

        for cmd in self.commands:
            dispatcher.add_handler(CommandHandler(cmd, self._command_hook(cmd)))

        self.logger.info('Initialized Telegram backend')
        telegram.start_polling()


# vim:sw=4:ts=4:et:
