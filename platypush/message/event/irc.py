from abc import ABC
from base64 import b64encode
from typing import Optional

from platypush.message.event import Event


class IRCEvent(Event, ABC):
    """
    IRC base event.
    """
    def __init__(self, *args, server: Optional[str] = None, port: Optional[int] = None,
                 alias: Optional[str] = None, channel: Optional[str] = None, **kwargs):
        super().__init__(*args, server=server, port=port, alias=alias, channel=channel, **kwargs)


class IRCChannelJoinEvent(IRCEvent):
    """
    Event triggered upon account channel join.
    """
    def __init__(self, *args, nick: str, **kwargs):
        super().__init__(*args, nick=nick, **kwargs)


class IRCChannelKickEvent(IRCEvent):
    """
    Event triggered upon account channel kick.
    """
    def __init__(self, *args, target_nick: str, source_nick: Optional[str] = None, **kwargs):
        super().__init__(*args, source_nick=source_nick, target_nick=target_nick, **kwargs)


class IRCModeEvent(IRCEvent):
    """
    Event triggered when the IRC mode of a channel user changes.
    """
    def __init__(
            self, *args, mode: str, channel: Optional[str] = None,
            source: Optional[str] = None,
            target_: Optional[str] = None, **kwargs
    ):
        super().__init__(*args, mode=mode, channel=channel, source=source, target_=target_, **kwargs)


class IRCPartEvent(IRCEvent):
    """
    Event triggered when an IRC nick parts.
    """
    def __init__(self, *args, nick: str, **kwargs):
        super().__init__(*args, nick=nick, **kwargs)


class IRCQuitEvent(IRCEvent):
    """
    Event triggered when an IRC nick quits.
    """
    def __init__(self, *args, nick: str, **kwargs):
        super().__init__(*args, nick=nick, **kwargs)


class IRCNickChangeEvent(IRCEvent):
    """
    Event triggered when a IRC nick changes.
    """
    def __init__(self, *args, before: str, after: str, **kwargs):
        super().__init__(*args, before=before, after=after, **kwargs)


class IRCConnectEvent(IRCEvent):
    """
    Event triggered upon server connection.
    """


class IRCDisconnectEvent(IRCEvent):
    """
    Event triggered upon server disconnection.
    """


class IRCPrivateMessageEvent(IRCEvent):
    """
    Event triggered when a private message is received.
    """
    def __init__(self, *args, text: str, nick: str, mentions_me: bool = False, **kwargs):
        super().__init__(*args, text=text, nick=nick, mentions_me=mentions_me, **kwargs)


class IRCPublicMessageEvent(IRCEvent):
    """
    Event triggered when a public message is received.
    """
    def __init__(self, *args, text: str, nick: str, mentions_me: bool = False, **kwargs):
        super().__init__(*args, text=text, nick=nick, mentions_me=mentions_me, **kwargs)


class IRCDCCRequestEvent(IRCEvent):
    """
    Event triggered when a DCC connection request is received.
    """
    def __init__(self, *args, address: str, port: int, nick: str, **kwargs):
        super().__init__(*args, address=address, port=port, nick=nick, **kwargs)


class IRCDCCMessageEvent(IRCEvent):
    """
    Event triggered when a DCC message is received.
    """
    def __init__(self, *args, address: str, body: bytes, **kwargs):
        super().__init__(
            *args, address=address, body=b64encode(body).decode(), **kwargs
        )


class IRCCTCPMessageEvent(IRCEvent):
    """
    Event triggered when a CTCP message is received.
    """
    def __init__(self, *args, address: str, message: str, **kwargs):
        super().__init__(*args, address=address, message=message, **kwargs)


class IRCDCCFileRequestEvent(IRCEvent):
    """
    Event triggered when a DCC file send request is received.
    """
    def __init__(
            self, *args, nick: str, address: str, file: str,
            port: int, size: Optional[int] = None, **kwargs
    ):
        super().__init__(
            *args, nick=nick, address=address, file=file, port=port,
            size=size, **kwargs
        )


class IRCDCCFileRecvCompletedEvent(IRCEvent):
    """
    Event triggered when a DCC file transfer RECV is completed.
    """
    def __init__(
            self, *args, address: str, port: int, file: str,
            size: Optional[int] = None, **kwargs
    ):
        super().__init__(
            *args, address=address, file=file,
            port=port, size=size, **kwargs
        )


class IRCDCCFileRecvCancelledEvent(IRCEvent):
    """
    Event triggered when a DCC file transfer RECV is cancelled.
    """
    def __init__(
            self, *args, address: str, port: int, file: str,
            error: str, **kwargs
    ):
        super().__init__(
            *args, address=address, file=file, port=port,
            error=error, **kwargs
        )


class IRCDCCFileSendCompletedEvent(IRCEvent):
    """
    Event triggered when a DCC file transfer SEND is completed.
    """
    def __init__(self, *args, address: str, port: int, file: str, **kwargs):
        super().__init__(*args, address=address, file=file, port=port, **kwargs)


class IRCDCCFileSendCancelledEvent(IRCEvent):
    """
    Event triggered when a DCC file transfer SEND is cancelled.
    """
    def __init__(
            self, *args, address: str, port: int, file: str,
            error: str, **kwargs
    ):
        super().__init__(
            *args, address=address, file=file, port=port,
            error=error, **kwargs
        )
