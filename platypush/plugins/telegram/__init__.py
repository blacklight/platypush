import datetime
import logging

from multiprocessing import Queue as PQueue
from queue import Empty, Queue as TQueue
from typing import Dict, List, Optional, Union
from uuid import UUID

from platypush.plugins import RunnablePlugin, action
from platypush.plugins.chat import ChatPlugin
from platypush.schemas.telegram import (
    TelegramChatSchema,
    TelegramFileSchema,
)
from platypush.utils import wait_for_either

from ._bridge import ResultBridge
from ._model import Command, Resource, END_OF_SERVICE
from ._service import TelegramService
from ._utils import dump_msg, dump_user


class TelegramPlugin(ChatPlugin, RunnablePlugin):
    """
    Plugin to programmatically send Telegram messages through a Telegram bot.
    In order to send messages to contacts, groups or channels you'll first need
    to register a bot. To do so:

        1. Open a Telegram conversation with the `@BotFather
           <https://telegram.me/BotFather>`_.
        2. Send ``/start`` followed by ``/newbot``. Choose a display name and a
           username for your bot.
        3. Copy the provided API token in the configuration of this plugin.
        4. Open a conversation with your newly created bot.

    """

    _DEFAULT_TIMEOUT = 20

    def __init__(
        self,
        api_token: str,
        authorized_chat_ids: Optional[List[Union[str, int]]] = None,
        **kwargs,
    ):
        """
        :param api_token: API token as returned by the `@BotFather
            <https://telegram.me/BotFather>`_
        :param authorized_chat_ids: Optional list of chat_id/user_id which are
            authorized to send messages to the bot. If nothing is specified
            then no restrictions are applied.
        """
        super().__init__(**kwargs)
        self._authorized_chat_ids = set(authorized_chat_ids or [])
        self._api_token = api_token
        self._cmd_queue = PQueue()
        self._result_queue = PQueue()
        self._service: Optional[TelegramService] = None
        self._response_queues: Dict[UUID, TQueue] = {}
        self._result_bridge: Optional[ResultBridge] = None

        # Set httpx logging to WARNING, or it will log a line for every request
        logging.getLogger("httpx").setLevel(logging.WARNING)

    def _exec(
        self, cmd: str, *args, timeout: Optional[float] = _DEFAULT_TIMEOUT, **kwargs
    ):
        assert self._service, "Telegram service not running"
        cmd_obj = Command(cmd, args=args, kwargs=kwargs, timeout=timeout)
        self._response_queues[cmd_obj.id] = TQueue()
        self._cmd_queue.put_nowait(cmd_obj)

        try:
            result = self._response_queues[cmd_obj.id].get(timeout=timeout)
        except (TimeoutError, Empty) as e:
            raise TimeoutError(f"Timeout while executing command {cmd}") from e
        finally:
            self._response_queues.pop(cmd_obj.id, None)

        assert not isinstance(
            result, Exception
        ), f'Error while executing command {cmd}: {result}'

        return result

    @property
    def response_queues(self):
        return self._response_queues

    @property
    def result_queue(self):
        return self._result_queue

    @action
    def send_message(  # pylint: disable=arguments-differ
        self,
        chat_id: Union[str, int],
        text: str,
        *_,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
        **__,
    ) -> dict:
        """
        Send a message to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param text: Text to be sent.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_web_page_preview: If True then web previews for URLs
            will be disabled.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Request timeout (default: 20 seconds).
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_message',
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
            )
        )

    @action
    def send_photo(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send a picture to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or
            ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param caption: Optional caption for the picture.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_photo',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='photo',
                caption=caption,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
                parse_mode=parse_mode,
            )
        )

    @action
    def send_audio(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        caption: Optional[str] = None,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        duration: Optional[float] = None,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send audio to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or
            ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param caption: Optional caption for the picture.
        :param performer: Optional audio performer.
        :param title: Optional audio title.
        :param duration: Duration of the audio in seconds.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_audio',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='audio',
                caption=caption,
                disable_notification=disable_notification,
                performer=performer,
                title=title,
                duration=duration,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
                parse_mode=parse_mode,
            )
        )

    @action
    def send_document(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send a document to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or
            ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param filename: Name of the file as it will be shown in Telegram.
        :param caption: Optional caption for the picture.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_document',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='document',
                filename=filename,
                caption=caption,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
                parse_mode=parse_mode,
            )
        )

    @action
    def send_video(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        duration: Optional[int] = None,
        caption: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send a video to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or
            ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param duration: Duration in seconds.
        :param caption: Optional caption for the picture.
        :param width: Video width.
        :param height: Video height.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_video',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='video',
                duration=duration,
                caption=caption,
                width=width,
                height=height,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
                parse_mode=parse_mode,
            )
        )

    @action
    def send_animation(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        duration: Optional[int] = None,
        caption: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send an animation (GIF or H.264/MPEG-4 AVC video without sound) to a
        chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or
            ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param duration: Duration in seconds.
        :param caption: Optional caption for the picture.
        :param width: Video width.
        :param height: Video height.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_animation',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='animation',
                duration=duration,
                caption=caption,
                width=width,
                height=height,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
                parse_mode=parse_mode,
            )
        )

    @action
    def send_voice(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        caption: Optional[str] = None,
        duration: Optional[float] = None,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send audio to a chat as a voice file. For this to work, your audio must
        be in an .ogg file encoded with OPUS (other formats may be sent as
        Audio or Document).

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param caption: Optional caption for the picture.
        :param duration: Duration of the voice in seconds.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown
            or HTML content.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_voice',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='voice',
                caption=caption,
                disable_notification=disable_notification,
                duration=duration,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
                parse_mode=parse_mode,
            )
        )

    @action
    def send_video_note(
        self,
        chat_id: Union[str, int],
        file_id: Optional[int] = None,
        url: Optional[str] = None,
        path: Optional[str] = None,
        duration: Optional[int] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send a video note to a chat. As of v.4.0, Telegram clients support
        rounded square mp4 videos of up to 1 minute long.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param file_id: Set it if the file already exists on Telegram servers
            and has a file_id. Note that you'll have to specify either
            ``file_id``, ``url`` or ``path``.
        :param url: Set it if you want to send a file from a remote URL. Note
            that you'll have to specify either ``file_id``, ``url`` or
            ``path``.
        :param path: Set it if you want to send a file from the local
            filesystem. Note that you'll have to specify either ``file_id``,
            ``url`` or ``path``.
        :param duration: Duration in seconds.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_video_note',
                chat_id=chat_id,
                resource=Resource(file_id=file_id, url=url, path=path),
                resource_attr='video',
                duration=duration,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
            )
        )

    @action
    def send_location(
        self,
        chat_id: Union[str, int],
        latitude: float,
        longitude: float,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send a location to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param latitude: Latitude
        :param longitude: Longitude
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_location',
                chat_id=chat_id,
                latitude=latitude,
                longitude=longitude,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
            )
        )

    @action
    def send_venue(
        self,
        chat_id: Union[str, int],
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: Optional[str] = None,
        foursquare_type: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send the address of a venue to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param latitude: Latitude
        :param longitude: Longitude
        :param title: Venue name.
        :param address: Venue address.
        :param foursquare_id: Foursquare ID.
        :param foursquare_type: Foursquare type.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_venue',
                chat_id=chat_id,
                latitude=latitude,
                longitude=longitude,
                title=title,
                address=address,
                foursquare_id=foursquare_id,
                foursquare_type=foursquare_type,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
            )
        )

    @action
    def send_contact(
        self,
        chat_id: Union[str, int],
        phone_number: str,
        first_name: str,
        last_name: Optional[str] = None,
        vcard: Optional[str] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Send a contact to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param phone_number: Phone number.
        :param first_name: First name.
        :param last_name: Last name.
        :param vcard: Additional contact info in vCard format (0-2048 bytes).
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param reply_to_message_id: If set then the message will be sent as a
            response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        :return: .. schema:: telegram.TelegramMessageSchema
        """
        return dump_msg(
            self._exec(
                'send_contact',
                chat_id=chat_id,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                vcard=vcard,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                timeout=timeout,
            )
        )

    @action
    def get_file(self, file_id: str, timeout: Optional[float] = None) -> dict:
        """
        Get the info and URL of an uploaded file by file_id.

        :param file_id: File ID.
        :param timeout: Upload timeout (default: 20 seconds).
        :return: .. schema:: telegram.TelegramFileSchema
        """
        return dict(
            TelegramFileSchema().dump(self._exec('get_file', file_id, timeout=timeout))
        )

    @action
    def get_chat(
        self, chat_id: Union[int, str], timeout: Optional[float] = _DEFAULT_TIMEOUT
    ) -> dict:
        """
        Get the info about a Telegram chat.

        :param chat_id: Chat ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """
        return dict(
            TelegramChatSchema().dump(self._exec('get_chat', chat_id, timeout=timeout))
        )

    @action
    def get_chat_user(
        self,
        chat_id: Union[int, str],
        user_id: int,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ) -> dict:
        """
        Get the info about a user connected to a chat.

        :param chat_id: Chat ID.
        :param user_id: User ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """
        return dump_user(
            self._exec('get_chat_member', chat_id, user_id, timeout=timeout)
        )

    @action
    def get_chat_administrators(
        self, chat_id: Union[int, str], timeout: Optional[float] = _DEFAULT_TIMEOUT
    ) -> List[dict]:
        """
        Get the list of the administrators of a chat.

        :param chat_id: Chat ID.
        :param timeout: Upload timeout (default: 20 seconds).
        :return: .. schema:: telegram.TelegramUserSchema(many=True)
        """
        return [
            dump_user(user.user)
            for user in self._exec('get_chat_administrators', chat_id, timeout=timeout)
        ]

    @action
    def get_chat_members_count(
        self, chat_id: Union[int, str], timeout: Optional[float] = _DEFAULT_TIMEOUT
    ) -> int:
        """
        Get the number of users in a chat.

        :param chat_id: Chat ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """
        return self._exec('get_chat_members_count', chat_id, timeout=timeout)

    @action
    def kick_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        until_date: Optional[datetime.datetime] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Kick a user from a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param user_id: Unique user ID.
        :param until_date: End date for the ban.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'kick_chat_member',
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
            timeout=timeout,
        )

    @action
    def unban_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Lift the ban from a chat member.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param user_id: Unique user ID.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'unban_chat_member', chat_id=chat_id, user_id=user_id, timeout=timeout
        )

    @action
    def promote_chat_member(
        self,
        chat_id: Union[str, int],
        user_id: int,
        can_change_info: Optional[bool] = None,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_delete_messages: Optional[bool] = None,
        can_invite_users: Optional[bool] = None,
        can_restrict_members: Optional[bool] = None,
        can_promote_members: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Promote or demote a member.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param user_id: Unique user ID.
        :param can_change_info: Pass True if the user can change channel info.
        :param can_post_messages: Pass True if the user can post messages.
        :param can_edit_messages: Pass True if the user can edit messages.
        :param can_delete_messages: Pass True if the user can delete messages.
        :param can_invite_users: Pass True if the user can invite other users
            to the channel/group.
        :param can_restrict_members: Pass True if the user can restrict the
            permissions of other users.
        :param can_promote_members: Pass True if the user can promote mebmers.
        :param can_pin_messages: Pass True if the user can pin messages.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'promote_chat_member',
            chat_id=chat_id,
            user_id=user_id,
            can_change_info=can_change_info,
            can_post_messages=can_post_messages,
            can_edit_messages=can_edit_messages,
            can_delete_messages=can_delete_messages,
            can_invite_users=can_invite_users,
            can_restrict_members=can_restrict_members,
            can_promote_members=can_promote_members,
            can_pin_messages=can_pin_messages,
            timeout=timeout,
        )

    @action
    def set_chat_title(
        self,
        chat_id: Union[str, int],
        title: str,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Set the title of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param title: New chat title.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'set_chat_title', chat_id=chat_id, description=title, timeout=timeout
        )

    @action
    def set_chat_description(
        self,
        chat_id: Union[str, int],
        description: str,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Set the description of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param description: New chat description.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'set_chat_description',
            chat_id=chat_id,
            description=description,
            timeout=timeout,
        )

    @action
    def set_chat_photo(
        self,
        chat_id: Union[str, int],
        path: str,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Set the photo of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param path: Path of the new image.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'set_chat_photo',
            chat_id=chat_id,
            resource=Resource(path=path),
            resource_attr='photo',
            timeout=timeout,
        )

    @action
    def delete_chat_photo(
        self, chat_id: Union[str, int], timeout: Optional[float] = _DEFAULT_TIMEOUT
    ):
        """
        Delete the photo of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec('delete_chat_photo', chat_id=chat_id, timeout=timeout)

    @action
    def pin_chat_message(
        self,
        chat_id: Union[str, int],
        message_id: int,
        disable_notification: Optional[bool] = None,
        timeout: Optional[float] = _DEFAULT_TIMEOUT,
    ):
        """
        Pin a message in a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param message_id: Message ID.
        :param disable_notification: If True then no notification will be sent
            to the users.
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec(
            'pin_chat_message',
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
            timeout=timeout,
        )

    @action
    def unpin_chat_message(
        self, chat_id: Union[str, int], timeout: Optional[float] = _DEFAULT_TIMEOUT
    ):
        """
        Unpin the message of a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``. In order to get your own
            Telegram chat_id open a conversation with `@IDBot
            <https://telegram.me/IDBot>`_ and type ``/start`` followed by
            ``/getid``. Similar procedures also exist to get a group or channel
            chat_id - just Google for "Telegram get channel/group chat_id".
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec('unpin_chat_message', chat_id=chat_id, timeout=timeout)

    @action
    def leave_chat(
        self, chat_id: Union[str, int], timeout: Optional[float] = _DEFAULT_TIMEOUT
    ):
        """
        Leave a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique
            identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed
            by ``/getid``. Similar procedures also exist to get a group or
            channel chat_id - just Google for "Telegram get channel/group
            chat_id".
        :param timeout: Request timeout (default: 20 seconds)
        """
        self._exec('leave_chat', chat_id=chat_id, timeout=timeout)

    def main(self):
        self._result_bridge = ResultBridge(self)
        self._result_bridge.start()

        while not self.should_stop():
            self._service = TelegramService(
                self._api_token,
                cmd_queue=self._cmd_queue,
                result_queue=self._result_queue,
                authorized_chat_ids=self._authorized_chat_ids,
            )

            self._service.start()
            wait_for_either(self._should_stop, self._service.stop_event)
            self.wait_stop(10)

    def stop(self):
        # Send an END_OF_SERVICE to the result queue to signal that the service
        # is stopping
        self._cmd_queue.put_nowait(END_OF_SERVICE)

        if self._service:
            self._service.stop()
            self._service = None

        if self._result_bridge and self._result_bridge.is_alive():
            self._result_bridge.join()
            self._result_bridge = None

        super().stop()


# vim:sw=4:ts=4:et:
