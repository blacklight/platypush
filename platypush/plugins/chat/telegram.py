import datetime
import os

from threading import RLock
from typing import Optional, Union

# noinspection PyPackageRequirements
from telegram.ext import Updater
# noinspection PyPackageRequirements
from telegram.message import Message as TelegramMessage
# noinspection PyPackageRequirements
from telegram.user import User as TelegramUser

from platypush.message.response.chat.telegram import TelegramMessageResponse, TelegramFileResponse, \
    TelegramChatResponse, TelegramUserResponse, TelegramUsersResponse
from platypush.plugins import action
from platypush.plugins.chat import ChatPlugin


class Resource:
    def __init__(self, file_id: Optional[int] = None, url: Optional[str] = None, path: Optional[str] = None):
        assert file_id or url or path, 'You need to specify either file_id, url or path'
        self.file_id = file_id
        self.url = url
        self.path = path
        self._file = None

    def __enter__(self):
        if self.path:
            self._file = open(os.path.abspath(os.path.expanduser(self.path)), 'rb')
            return self._file

        return self.file_id or self.url

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            self._file.close()


class ChatTelegramPlugin(ChatPlugin):
    """
    Plugin to programmatically send Telegram messages through a Telegram bot. In order to send messages to contacts,
    groups or channels you'll first need to register a bot. To do so:

        1. Open a Telegram conversation with the `@BotFather <https://telegram.me/BotFather>`_.
        2. Send ``/start`` followed by ``/newbot``. Choose a display name and a username for your bot.
        3. Copy the provided API token in the configuration of this plugin.
        4. Open a conversation with your newly created bot.

    Requires:

        * **python-telegram-bot** (``pip install python-telegram-bot``)

    """

    def __init__(self, api_token: str, **kwargs):
        """
        :param api_token: API token as returned by the `@BotFather <https://telegram.me/BotFather>`_
        """
        super().__init__(**kwargs)

        self._api_token = api_token
        self._telegram_lock = RLock()
        self._telegram: Optional[Updater] = None

    def get_telegram(self) -> Updater:
        with self._telegram_lock:
            if self._telegram:
                return self._telegram

            self._telegram = Updater(self._api_token, use_context=True)
            return self._telegram

    @staticmethod
    def parse_msg(msg: TelegramMessage) -> TelegramMessageResponse:
        return TelegramMessageResponse(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            chat_username=msg.chat.username,
            chat_firstname=msg.chat.first_name,
            chat_lastname=msg.chat.last_name,
            from_user_id=msg.from_user.id if msg.from_user else None,
            from_username=msg.from_user.username if msg.from_user else None,
            from_firstname=msg.from_user.first_name if msg.from_user else None,
            from_lastname=msg.from_user.last_name if msg.from_user else None,
            text=msg.text,
            caption=msg.caption,
            creation_date=msg.date,
            edit_date=msg.edit_date,
            forward_date=msg.forward_date,
            forward_from_message_id=msg.forward_from_message_id,
            photo_file_id=msg.photo[0].file_id if msg.photo else None,
            photo_file_size=msg.photo[0].file_size if msg.photo else None,
            photo_width=msg.photo[0].width if msg.photo else None,
            photo_height=msg.photo[0].height if msg.photo else None,
            document_file_id=msg.document.file_id if msg.document else None,
            document_file_name=msg.document.file_name if msg.document else None,
            document_file_size=msg.document.file_size if msg.document else None,
            document_mime_type=msg.document.mime_type if msg.document else None,
            audio_file_id=msg.audio.file_id if msg.audio else None,
            audio_file_size=msg.audio.file_size if msg.audio else None,
            audio_performer=msg.audio.performer if msg.audio else None,
            audio_title=msg.audio.title if msg.audio else None,
            audio_duration=msg.audio.duration if msg.audio else None,
            audio_mime_type=msg.audio.mime_type if msg.audio else None,
            video_file_id=msg.video.file_id if msg.video else None,
            video_file_size=msg.video.file_size if msg.video else None,
            video_duration=msg.video.duration if msg.video else None,
            video_width=msg.video.width if msg.video else None,
            video_height=msg.video.height if msg.video else None,
            video_mime_type=msg.video.mime_type if msg.video else None,
            location_latitude=msg.location.latitude if msg.location else None,
            location_longitude=msg.location.longitude if msg.location else None,
            contact_phone_number=msg.contact.phone_number if msg.contact else None,
            contact_first_name=msg.contact.first_name if msg.contact else None,
            contact_last_name=msg.contact.last_name if msg.contact else None,
            contact_user_id=msg.contact.user_id if msg.contact else None,
            contact_vcard=msg.contact.vcard if msg.contact else None,
            link=msg.link,
            media_group_id=msg.media_group_id
        )

    @staticmethod
    def parse_user(user: TelegramUser) -> TelegramUserResponse:
        return TelegramUserResponse(
            user_id=user.id,
            username=user.username,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            link=user.link
        )

    @action
    def send_message(self, chat_id: Union[str, int], text: str, parse_mode: Optional[str] = None,
                     disable_web_page_preview: bool = False, disable_notification: bool = False,
                     reply_to_message_id: Optional[int] = None) -> TelegramMessageResponse:
        """
        Send a message to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param text: Text to be sent.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_web_page_preview: If True then web previews for URLs will be disabled.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        """

        telegram = self.get_telegram()
        msg = telegram.bot.send_message(chat_id=chat_id,
                                        text=text,
                                        parse_mode=parse_mode,
                                        disable_web_page_preview=disable_web_page_preview,
                                        disable_notification=disable_notification,
                                        reply_to_message_id=reply_to_message_id)

        return self.parse_msg(msg)

    @action
    def send_photo(self, chat_id: Union[str, int],
                   file_id: Optional[int] = None,
                   url: Optional[str] = None,
                   path: Optional[str] = None,
                   caption: Optional[str] = None,
                   parse_mode: Optional[str] = None,
                   disable_notification: bool = False,
                   reply_to_message_id: Optional[int] = None,
                   timeout: int = 20) -> TelegramMessageResponse:
        """
        Send a picture to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param caption: Optional caption for the picture.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_photo(chat_id=chat_id,
                                          photo=resource,
                                          caption=caption,
                                          disable_notification=disable_notification,
                                          reply_to_message_id=reply_to_message_id,
                                          timeout=timeout, parse_mode=parse_mode)

        return self.parse_msg(msg)

    @action
    def send_audio(self, chat_id: Union[str, int],
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
                   timeout: int = 20) -> TelegramMessageResponse:
        """
        Send audio to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param caption: Optional caption for the picture.
        :param performer: Optional audio performer.
        :param title: Optional audio title.
        :param duration: Duration of the audio in seconds.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_audio(chat_id=chat_id,
                                          audio=resource,
                                          caption=caption,
                                          disable_notification=disable_notification,
                                          performer=performer,
                                          title=title,
                                          duration=duration,
                                          reply_to_message_id=reply_to_message_id,
                                          timeout=timeout,
                                          parse_mode=parse_mode)

        return self.parse_msg(msg)

    @action
    def send_document(self, chat_id: Union[str, int],
                      file_id: Optional[int] = None,
                      url: Optional[str] = None,
                      path: Optional[str] = None,
                      filename: Optional[str] = None,
                      caption: Optional[str] = None,
                      parse_mode: Optional[str] = None,
                      disable_notification: bool = False,
                      reply_to_message_id: Optional[int] = None,
                      timeout: int = 20) -> TelegramMessageResponse:
        """
        Send a document to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param filename: Name of the file as it will be shown in Telegram.
        :param caption: Optional caption for the picture.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_document(chat_id=chat_id,
                                             document=resource,
                                             filename=filename,
                                             caption=caption,
                                             disable_notification=disable_notification,
                                             reply_to_message_id=reply_to_message_id,
                                             timeout=timeout,
                                             parse_mode=parse_mode)

        return self.parse_msg(msg)

    @action
    def send_video(self, chat_id: Union[str, int],
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
                   timeout: int = 20) -> TelegramMessageResponse:
        """
        Send a video to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param duration: Duration in seconds.
        :param caption: Optional caption for the picture.
        :param width: Video width.
        :param height: Video height.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_video(chat_id=chat_id,
                                          video=resource,
                                          duration=duration,
                                          caption=caption,
                                          width=width,
                                          height=height,
                                          disable_notification=disable_notification,
                                          reply_to_message_id=reply_to_message_id,
                                          timeout=timeout,
                                          parse_mode=parse_mode)

        return self.parse_msg(msg)

    @action
    def send_animation(self, chat_id: Union[str, int],
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
                       timeout: int = 20) -> TelegramMessageResponse:
        """
        Send an animation (GIF or H.264/MPEG-4 AVC video without sound) to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param duration: Duration in seconds.
        :param caption: Optional caption for the picture.
        :param width: Video width.
        :param height: Video height.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_animation(chat_id=chat_id,
                                              animation=resource,
                                              duration=duration,
                                              caption=caption,
                                              width=width,
                                              height=height,
                                              disable_notification=disable_notification,
                                              reply_to_message_id=reply_to_message_id,
                                              timeout=timeout,
                                              parse_mode=parse_mode)

        return self.parse_msg(msg)

    @action
    def send_voice(self, chat_id: Union[str, int],
                   file_id: Optional[int] = None,
                   url: Optional[str] = None,
                   path: Optional[str] = None,
                   caption: Optional[str] = None,
                   duration: Optional[float] = None,
                   parse_mode: Optional[str] = None,
                   disable_notification: bool = False,
                   reply_to_message_id: Optional[int] = None,
                   timeout: int = 20) -> TelegramMessageResponse:
        """
        Send audio to a chat as a voice file. For this to work, your audio must be in an .ogg file encoded with OPUS
        (other formats may be sent as Audio or Document).

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param caption: Optional caption for the picture.
        :param duration: Duration of the voice in seconds.
        :param parse_mode: Set to 'Markdown' or 'HTML' to send either Markdown or HTML content.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_voice(chat_id=chat_id,
                                          voice=resource,
                                          caption=caption,
                                          disable_notification=disable_notification,
                                          duration=duration,
                                          reply_to_message_id=reply_to_message_id,
                                          timeout=timeout, parse_mode=parse_mode)

        return self.parse_msg(msg)

    @action
    def send_video_note(self, chat_id: Union[str, int],
                        file_id: Optional[int] = None,
                        url: Optional[str] = None,
                        path: Optional[str] = None,
                        duration: Optional[int] = None,
                        disable_notification: bool = False,
                        reply_to_message_id: Optional[int] = None,
                        timeout: int = 20) -> TelegramMessageResponse:
        """
        Send a video note to a chat. As of v.4.0, Telegram clients support rounded square mp4 videos of up to
        1 minute long.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param file_id: Set it if the file already exists on Telegram servers and has a file_id.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param url: Set it if you want to send a file from a remote URL.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param path: Set it if you want to send a file from the local filesystem.
            Note that you'll have to specify either ``file_id``, ``url`` or ``path``.

        :param duration: Duration in seconds.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(file_id=file_id, url=url, path=path) as resource:
            msg = telegram.bot.send_video_note(chat_id=chat_id,
                                               video=resource,
                                               duration=duration,
                                               disable_notification=disable_notification,
                                               reply_to_message_id=reply_to_message_id,
                                               timeout=timeout)

        return self.parse_msg(msg)

    @action
    def send_location(self, chat_id: Union[str, int],
                      latitude: float,
                      longitude: float,
                      disable_notification: bool = False,
                      reply_to_message_id: Optional[int] = None,
                      timeout: int = 20) -> TelegramMessageResponse:
        """
        Send a location to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param latitude: Latitude
        :param longitude: Longitude
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        msg = telegram.bot.send_location(chat_id=chat_id,
                                         latitude=latitude,
                                         longitude=longitude,
                                         disable_notification=disable_notification,
                                         reply_to_message_id=reply_to_message_id,
                                         timeout=timeout)

        return self.parse_msg(msg)

    @action
    def send_venue(self, chat_id: Union[str, int],
                   latitude: float,
                   longitude: float,
                   title: str,
                   address: str,
                   foursquare_id: Optional[str] = None,
                   foursquare_type: Optional[str] = None,
                   disable_notification: bool = False,
                   reply_to_message_id: Optional[int] = None,
                   timeout: int = 20) -> TelegramMessageResponse:
        """
        Send the address of a venue to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param latitude: Latitude
        :param longitude: Longitude
        :param title: Venue name.
        :param address: Venue address.
        :param foursquare_id: Foursquare ID.
        :param foursquare_type: Foursquare type.
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        msg = telegram.bot.send_venue(chat_id=chat_id,
                                      latitude=latitude,
                                      longitude=longitude,
                                      title=title,
                                      address=address,
                                      foursquare_id=foursquare_id,
                                      foursquare_type=foursquare_type,
                                      disable_notification=disable_notification,
                                      reply_to_message_id=reply_to_message_id,
                                      timeout=timeout)

        return self.parse_msg(msg)

    @action
    def send_contact(self, chat_id: Union[str, int],
                     phone_number: str,
                     first_name: str,
                     last_name: Optional[str] = None,
                     vcard: Optional[str] = None,
                     disable_notification: bool = False,
                     reply_to_message_id: Optional[int] = None,
                     timeout: int = 20) -> TelegramMessageResponse:
        """
        Send a contact to a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param phone_number: Phone number.
        :param first_name: First name.
        :param last_name: Last name.
        :param vcard: Additional contact info in vCard format (0-2048 bytes).
        :param disable_notification: If True then no notification will be sent to the users.
        :param reply_to_message_id: If set then the message will be sent as a response to the specified message.
        :param timeout: Upload timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        msg = telegram.bot.send_contact(chat_id=chat_id,
                                        phone_number=phone_number,
                                        first_name=first_name,
                                        last_name=last_name,
                                        vcard=vcard,
                                        disable_notification=disable_notification,
                                        reply_to_message_id=reply_to_message_id,
                                        timeout=timeout)

        return self.parse_msg(msg)

    @action
    def get_file(self, file_id: str, timeout: int = 20) -> TelegramFileResponse:
        """
        Get the info and URL of an uploaded file by file_id.

        :param file_id: File ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """

        telegram = self.get_telegram()
        file = telegram.bot.get_file(file_id, timeout=timeout)
        return TelegramFileResponse(file_id=file.file_id, file_path=file.file_path, file_size=file.file_size)

    @action
    def get_chat(self, chat_id: Union[int, str], timeout: int = 20) -> TelegramChatResponse:
        """
        Get the info about a Telegram chat.

        :param chat_id: Chat ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """

        telegram = self.get_telegram()
        chat = telegram.bot.get_chat(chat_id, timeout=timeout)
        return TelegramChatResponse(chat_id=chat.id,
                                    link=chat.link,
                                    username=chat.username,
                                    invite_link=chat.invite_link,
                                    title=chat.title,
                                    description=chat.description,
                                    type=chat.type,
                                    first_name=chat.first_name,
                                    last_name=chat.last_name)

    @action
    def get_chat_user(self, chat_id: Union[int, str], user_id: int, timeout: int = 20) -> TelegramUserResponse:
        """
        Get the info about a user connected to a chat.

        :param chat_id: Chat ID.
        :param user_id: User ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """

        telegram = self.get_telegram()
        user = telegram.bot.get_chat_member(chat_id, user_id, timeout=timeout)
        return TelegramUserResponse(user_id=user.user.id,
                                    link=user.user.link,
                                    username=user.user.username,
                                    first_name=user.user.first_name,
                                    last_name=user.user.last_name,
                                    is_bot=user.user.is_bot,
                                    language_code=user.user.language_code)

    @action
    def get_chat_administrators(self, chat_id: Union[int, str], timeout: int = 20) -> TelegramUsersResponse:
        """
        Get the list of the administrators of a chat.

        :param chat_id: Chat ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """

        telegram = self.get_telegram()
        admins = telegram.bot.get_chat_administrators(chat_id, timeout=timeout)
        return TelegramUsersResponse([
            TelegramUserResponse(
                user_id=user.user.id,
                link=user.user.link,
                username=user.user.username,
                first_name=user.user.first_name,
                last_name=user.user.last_name,
                is_bot=user.user.is_bot,
                language_code=user.user.language_code,
            ) for user in admins
        ])

    @action
    def get_chat_members_count(self, chat_id: Union[int, str], timeout: int = 20) -> int:
        """
        Get the number of users in a chat.

        :param chat_id: Chat ID.
        :param timeout: Upload timeout (default: 20 seconds).
        """
        telegram = self.get_telegram()
        return telegram.bot.get_chat_members_count(chat_id, timeout=timeout)

    @action
    def kick_chat_member(self, chat_id: Union[str, int],
                         user_id: int,
                         until_date: Optional[datetime.datetime] = None,
                         timeout: int = 20):
        """
        Kick a user from a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param user_id: Unique user ID.
        :param until_date: End date for the ban.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.kick_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
            timeout=timeout)

    @action
    def unban_chat_member(self, chat_id: Union[str, int],
                          user_id: int,
                          timeout: int = 20):
        """
        Lift the ban from a chat member.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param user_id: Unique user ID.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.unban_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            timeout=timeout)

    @action
    def promote_chat_member(self, chat_id: Union[str, int],
                            user_id: int,
                            can_change_info: Optional[bool] = None,
                            can_post_messages: Optional[bool] = None,
                            can_edit_messages: Optional[bool] = None,
                            can_delete_messages: Optional[bool] = None,
                            can_invite_users: Optional[bool] = None,
                            can_restrict_members: Optional[bool] = None,
                            can_promote_members: Optional[bool] = None,
                            can_pin_messages: Optional[bool] = None,
                            timeout: int = 20):
        """
        Promote or demote a member.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param user_id: Unique user ID.
        :param can_change_info: Pass True if the user can change channel info.
        :param can_post_messages: Pass True if the user can post messages.
        :param can_edit_messages: Pass True if the user can edit messages.
        :param can_delete_messages: Pass True if the user can delete messages.
        :param can_invite_users: Pass True if the user can invite other users to the channel/group.
        :param can_restrict_members: Pass True if the user can restrict the permissions of other users.
        :param can_promote_members: Pass True if the user can promote mebmers.
        :param can_pin_messages: Pass True if the user can pin messages.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.promote_chat_member(
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
            timeout=timeout)

    @action
    def set_chat_title(self, chat_id: Union[str, int],
                       title: str,
                       timeout: int = 20):
        """
        Set the title of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param title: New chat title.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.set_chat_title(
            chat_id=chat_id,
            description=title,
            timeout=timeout)

    @action
    def set_chat_description(self, chat_id: Union[str, int],
                             description: str,
                             timeout: int = 20):
        """
        Set the description of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param description: New chat description.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.set_chat_description(
            chat_id=chat_id,
            description=description,
            timeout=timeout)

    @action
    def set_chat_photo(self, chat_id: Union[str, int],
                       path: str,
                       timeout: int = 20):
        """
        Set the photo of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param path: Path of the new image.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()

        with Resource(path=path) as resource:
            telegram.bot.set_chat_photo(
                chat_id=chat_id,
                photo=resource,
                timeout=timeout)

    @action
    def delete_chat_photo(self, chat_id: Union[str, int],
                          timeout: int = 20):
        """
        Delete the photo of a channel/group.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.delete_chat_photo(
            chat_id=chat_id,
            timeout=timeout)

    @action
    def pin_chat_message(self, chat_id: Union[str, int],
                         message_id: int,
                         disable_notification: Optional[bool] = None,
                         timeout: int = 20):
        """
        Pin a message in a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param message_id: Message ID.
        :param disable_notification: If True then no notification will be sent to the users.
        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.pin_chat_message(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
            timeout=timeout)

    @action
    def unpin_chat_message(self, chat_id: Union[str, int],
                           timeout: int = 20):
        """
        Unpin the message of a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.unpin_chat_message(
            chat_id=chat_id,
            timeout=timeout)

    @action
    def leave_chat(self, chat_id: Union[str, int],
                   timeout: int = 20):
        """
        Leave a chat.

        :param chat_id: Chat ID. Can be either a numerical ID or a unique identifier in the format ``@channelname``.
            In order to get your own Telegram chat_id open a conversation with
            `@IDBot <https://telegram.me/IDBot>`_ and type ``/start`` followed by ``/getid``. Similar procedures
            also exist to get a group or channel chat_id - just Google for "Telegram get channel/group chat_id".

        :param timeout: Request timeout (default: 20 seconds)
        """

        telegram = self.get_telegram()
        telegram.bot.leave_chat(
            chat_id=chat_id,
            timeout=timeout)


# vim:sw=4:ts=4:et:
