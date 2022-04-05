import os
from typing import Sequence, Dict, Tuple, Union, Optional

from platypush.plugins import RunnablePlugin, action
from platypush.schemas.irc import (
    IRCServerSchema,
    IRCServerStatusSchema,
    IRCChannelSchema,
)

from ._bot import IRCBot
from .. import ChatPlugin


class ChatIrcPlugin(RunnablePlugin, ChatPlugin):
    """
    IRC integration.

    This plugin allows you to easily create IRC bots with custom logic that reacts to IRC events
    and interact with IRC sessions.

    Triggers:

        * :class:`platypush.message.event.irc.IRCChannelJoinEvent` when a user joins a channel.
        * :class:`platypush.message.event.irc.IRCChannelKickEvent` when a user is kicked from a channel.
        * :class:`platypush.message.event.irc.IRCModeEvent` when a user/channel mode change event occurs.
        * :class:`platypush.message.event.irc.IRCPartEvent` when a user parts a channel.
        * :class:`platypush.message.event.irc.IRCQuitEvent` when a user quits.
        * :class:`platypush.message.event.irc.IRCNickChangeEvent` when a user nick changes.
        * :class:`platypush.message.event.irc.IRCConnectEvent` when the bot connects to a server.
        * :class:`platypush.message.event.irc.IRCDisconnectEvent` when the bot disconnects from a server.
        * :class:`platypush.message.event.irc.IRCPrivateMessageEvent` when a private message is received.
        * :class:`platypush.message.event.irc.IRCPublicMessageEvent` when a public message is received.
        * :class:`platypush.message.event.irc.IRCDCCRequestEvent` when a DCC connection request is received.
        * :class:`platypush.message.event.irc.IRCDCCMessageEvent` when a DCC message is received.
        * :class:`platypush.message.event.irc.IRCCTCPMessageEvent` when a CTCP message is received.
        * :class:`platypush.message.event.irc.IRCDCCFileRequestEvent` when a DCC file request is received.
        * :class:`platypush.message.event.irc.IRCDCCFileRecvCompletedEvent` when a DCC file download is completed.
        * :class:`platypush.message.event.irc.IRCDCCFileRecvCancelledEvent` when a DCC file download is cancelled.
        * :class:`platypush.message.event.irc.IRCDCCFileSendCompletedEvent` when a DCC file upload is completed.
        * :class:`platypush.message.event.irc.IRCDCCFileSendCancelledEvent` when a DCC file upload is cancelled.

    Requires:

        * **irc** (``pip install irc``)

    """

    def __init__(self, servers: Sequence[dict], **kwargs):
        """
        :param servers: List of servers/channels that the bot will automatically connect/join.
        """
        super().__init__(**kwargs)
        try:
            self._bots: Dict[Tuple[str, int], IRCBot] = {
                (server_conf['server'], server_conf['port']): IRCBot(**server_conf)
                for server_conf in IRCServerSchema().load(servers, many=True)
            }
        except Exception as e:
            self.logger.warning(f'Could not load IRC server configuration: {e}')
            self.logger.exception(e)
            raise e

    @property
    def _bots_by_server(self) -> Dict[str, IRCBot]:
        return {bot.server: bot for srv, bot in self._bots.items()}

    @property
    def _bots_by_server_and_port(self) -> Dict[Tuple[str, int], IRCBot]:
        return {(bot.server, bot.port): bot for srv, bot in self._bots.items()}

    @property
    def _bots_by_alias(self) -> Dict[str, IRCBot]:
        return {bot.alias: bot for srv, bot in self._bots.items() if bot.alias}

    def main(self):
        self._connect()
        self.wait_stop()

    def _connect(self):
        for srv, bot in self._bots.items():
            self.logger.info(f'Connecting to IRC server {srv}')
            bot.start()

    def stop(self):
        for srv, bot in self._bots.items():
            self.logger.info(f'Disconnecting from IRC server {srv}')
            try:
                bot.stop(bot.stop_message or 'Application stopped')
            except Exception as e:
                self.logger.warning(f'Error while stopping connection to {srv}: {e}')

        super().stop()

    def _get_bot(self, server: Union[str, Tuple[str, int]]) -> IRCBot:
        if isinstance(server, (tuple, list, set)):
            bot = self._bots_by_server_and_port[tuple(server)]
        else:
            bot = self._bots_by_alias.get(server, self._bots_by_server.get(server))

        assert bot, f'Bot connection to {server} not found'
        return bot

    @action
    def send_file(
        self,
        file: str,
        server: Union[str, Tuple[str, int]],
        nick: str,
        bind_address: Optional[str] = None,
    ):
        """
        Send a file to an IRC user over DCC connection.
        Note that passive connections are currently not supported.

        :param file: Path of the file that should be transferred.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param nick: Target IRC nick.
        :param bind_address: DCC listen bind address (default: any).
        """
        file = os.path.expanduser(file)
        assert os.path.isfile(file), f'{file} is not a regular file'
        bot = self._get_bot(server)
        bot.dcc_file_transfer(file=file, nick=nick, bind_address=bind_address)

    @action
    def send_message(
        self,
        text: str,
        server: Union[str, Tuple[str, int]],
        target: Union[str, Sequence[str]],
    ):
        """
        Send a message to a channel or a nick.

        :param text: Message content.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param target: Message target (nick or channel). If it's a list then the message will be sent
            to multiple targets.
        """
        bot = self._get_bot(server)
        method = (
            bot.connection.privmsg
            if isinstance(target, str)
            else bot.connection.privmsg_many
        )
        method(target, text)

    @action
    def send_notice(self, text: str, server: Union[str, Tuple[str, int]], target: str):
        """
        Send a notice to a channel or a nick.

        :param text: Message content.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param target: Message target (nick or channel).
        """
        bot = self._get_bot(server)
        bot.connection.notice(target, text)

    @action
    def servers(self) -> Sequence[dict]:
        """
        Get information about the connected servers.

        :return: .. schema:: irc.IRCServerStatusSchema(many=True)
        """
        bots = self._bots_by_server.values()
        return IRCServerStatusSchema().dump(
            {
                'server': bot.server,
                'port': bot.port,
                'alias': bot.alias,
                'real_name': bot.connection.get_server_name(),
                'nickname': bot.connection.get_nickname(),
                'is_connected': bot.connection.is_connected(),
                'connected_channels': bot.channels.keys(),
            }
            for bot in bots
        )

    @action
    def channel(self, server: Union[str, Tuple[str, int]], channel: str) -> dict:
        """
        Get information about a connected channel.

        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param channel:
        :return: .. schema:: irc.IRCChannelSchema
        """
        bot = self._get_bot(server)
        channel_name = channel
        channel = bot.channels.get(channel)
        assert channel, f'Not connected to channel {channel}'
        return IRCChannelSchema().dump(
            {
                'is_invite_only': channel.is_invite_only(),
                'is_moderated': channel.is_moderated(),
                'is_protected': channel.is_protected(),
                'is_secret': channel.is_secret(),
                'name': channel_name,
                'modes': channel.modes,
                'opers': list(channel.opers()),
                'owners': channel.owners(),
                'users': list(channel.users()),
                'voiced': list(channel.voiced()),
            }
        )

    @action
    def send_ctcp_message(
        self,
        ctcp_type: str,
        body: str,
        server: Union[str, Tuple[str, int]],
        target: str,
    ):
        """
        Send a CTCP message to a target.

        :param ctcp_type: CTCP message type.
        :param body: Message content.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param target: Message target.
        """
        bot = self._get_bot(server)
        bot.connection.ctcp(ctcp_type, target, body)

    @action
    def send_ctcp_reply(
        self, body: str, server: Union[str, Tuple[str, int]], target: str
    ):
        """
        Send a CTCP REPLY command.

        :param body: Message content.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param target: Message target.
        """
        bot = self._get_bot(server)
        bot.connection.ctcp_reply(target, body)

    @action
    def disconnect(
        self, server: Union[str, Tuple[str, int]], message: Optional[str] = None
    ):
        """
        Disconnect from a server.

        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param message: Disconnect message (default: configured ``stop_message``.
        """
        bot = self._get_bot(server)
        bot.connection.disconnect(message or bot.stop_message)

    @action
    def invite(self, nick: str, channel: str, server: Union[str, Tuple[str, int]]):
        """
        Invite a nick to a channel.

        :param nick: Target IRC nick.
        :param channel: Target IRC channel.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        bot.connection.invite(nick, channel)

    @action
    def join(self, channel: str, server: Union[str, Tuple[str, int]]):
        """
        Join a channel.

        :param channel: Target IRC channel.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        bot.connection.join(channel)

    @action
    def kick(
        self,
        nick: str,
        channel: str,
        server: Union[str, Tuple[str, int]],
        reason: Optional[str] = None,
    ):
        """
        Kick a nick from a channel.

        :param nick: Target IRC nick.
        :param channel: Target IRC channel.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param reason: Kick reason.
        """
        bot = self._get_bot(server)
        bot.connection.kick(channel, nick, reason)

    @action
    def mode(self, target: str, command: str, server: Union[str, Tuple[str, int]]):
        """
        Send a MODE command on the selected target.

        :param target: IRC target.
        :param command: Mode command.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        bot.connection.mode(target, command)

    @action
    def set_nick(self, nick: str, server: Union[str, Tuple[str, int]]):
        """
        Set the IRC nick.

        :param nick: New IRC nick.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        bot.connection.nick(nick)

    @action
    def oper(self, nick: str, password: str, server: Union[str, Tuple[str, int]]):
        """
        Send an OPER command.

        :param nick: IRC nick.
        :param password: Nick password.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        bot.connection.oper(nick, password)

    @action
    def part(
        self,
        channel: Union[str, Sequence[str]],
        server: Union[str, Tuple[str, int]],
        message: Optional[str] = None,
    ):
        """
        Parts/exits a channel.

        :param channel: IRC channel (or list of channels).
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param message: Optional part message (default: same as the bot's ``stop_message``).
        """
        bot = self._get_bot(server)
        channels = [channel] if isinstance(channel, str) else channel
        bot.connection.part(channels=channels, message=message or bot.stop_message)

    @action
    def quit(self, server: Union[str, Tuple[str, int]], message: Optional[str] = None):
        """
        Send a QUIT command.

        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param message: Optional quit message (default: same as the bot's ``stop_message``).
        """
        bot = self._get_bot(server)
        bot.connection.quit(message=message or bot.stop_message)

    @action
    def send_raw(self, message: str, server: Union[str, Tuple[str, int]]):
        """
        Send a raw IRC message to a connected server.

        :param message: IRC message.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        bot.connection.send_raw(message)

    @action
    def topic(
        self,
        channel: str,
        server: Union[str, Tuple[str, int]],
        topic: Optional[str] = None,
    ) -> str:
        """
        Get/set the topic of an IRC channel.

        :param channel: IRC channel.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        :param topic: If specified, then set the new topic as channel topic.
            Otherwise, just return the current channel topic.
        """
        bot = self._get_bot(server)
        with bot.event_queue('currenttopic') as evt_queue:
            bot.connection.topic(channel, topic)
            evt = evt_queue.get(block=True, timeout=bot.response_timeout)
            return evt.arguments[1]

    @action
    def whois(self, target: str, server: Union[str, Tuple[str, int]]):
        """
        Send a WHOIS command for a target.

        :param target: IRC target.
        :param server: IRC server, identified either by ``alias`` or ``(server, port)`` tuple.
        """
        bot = self._get_bot(server)
        with bot.event_queue('whoisuser') as evt_queue:
            bot.connection.whois([target])
            evt = evt_queue.get(block=True, timeout=bot.response_timeout)
            return evt.arguments


# vim:sw=4:ts=4:et:
