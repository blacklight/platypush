import datetime

from typing import Optional, List

from platypush.message.response import Response


class TelegramMessageResponse(Response):
    def __init__(self,
                 message_id: int,
                 chat_id: int,
                 creation_date: Optional[datetime.datetime],
                 chat_username: Optional[str] = None,
                 chat_firstname: Optional[str] = None,
                 chat_lastname: Optional[str] = None,
                 from_user_id: Optional[int] = None,
                 from_username: Optional[str] = None,
                 from_firstname: Optional[str] = None,
                 from_lastname: Optional[str] = None,
                 text: Optional[str] = None,
                 caption: Optional[str] = None,
                 edit_date: Optional[datetime.datetime] = None,
                 forward_date: Optional[datetime.datetime] = None,
                 forward_from_message_id: Optional[int] = None,
                 photo_file_id: Optional[str] = None,
                 photo_file_size: Optional[int] = None,
                 photo_width: Optional[int] = None,
                 photo_height: Optional[int] = None,
                 document_file_id: Optional[str] = None,
                 document_file_name: Optional[str] = None,
                 document_file_size: Optional[str] = None,
                 document_mime_type: Optional[str] = None,
                 audio_file_id: Optional[str] = None,
                 audio_file_size: Optional[str] = None,
                 audio_mime_type: Optional[str] = None,
                 audio_performer: Optional[str] = None,
                 audio_title: Optional[str] = None,
                 audio_duration: Optional[str] = None,
                 location_latitude: Optional[float] = None,
                 location_longitude: Optional[float] = None,
                 contact_phone_number: Optional[str] = None,
                 contact_first_name: Optional[str] = None,
                 contact_last_name: Optional[str] = None,
                 contact_user_id: Optional[int] = None,
                 contact_vcard: Optional[str] = None,
                 video_file_id: Optional[str] = None,
                 video_file_size: Optional[int] = None,
                 video_width: Optional[int] = None,
                 video_height: Optional[int] = None,
                 video_mime_type: Optional[str] = None,
                 video_duration: Optional[str] = None,
                 link: Optional[str] = None,
                 media_group_id: Optional[int] = None,
                 *args, **kwargs):
        super().__init__(*args, output={
            'message_id': message_id,
            'chat_id': chat_id,
            'chat_username': chat_username,
            'chat_firstname': chat_firstname,
            'chat_lastname': chat_lastname,
            'from_user_id': from_user_id,
            'from_username': from_username,
            'from_firstname': from_firstname,
            'from_lastname': from_lastname,
            'text': text,
            'caption': caption,
            'creation_date': creation_date,
            'edit_date': edit_date,
            'forward_from_message_id': forward_from_message_id,
            'forward_date': forward_date,
            'photo_file_id': photo_file_id,
            'photo_file_size': photo_file_size,
            'photo_width': photo_width,
            'photo_height': photo_height,
            'document_file_id': document_file_id,
            'document_file_name': document_file_name,
            'document_file_size': document_file_size,
            'document_mime_type': document_mime_type,
            'audio_file_id': audio_file_id,
            'audio_file_size': audio_file_size,
            'audio_performer': audio_performer,
            'audio_title': audio_title,
            'audio_duration': audio_duration,
            'audio_mime_type': audio_mime_type,
            'video_file_id': video_file_id,
            'video_file_size': video_file_size,
            'video_width': video_width,
            'video_height': video_height,
            'video_duration': video_duration,
            'video_mime_type': video_mime_type,
            'link': link,
            'location_latitude': location_latitude,
            'location_longitude': location_longitude,
            'contact_phone_number': contact_phone_number,
            'contact_first_name': contact_first_name,
            'contact_last_name': contact_last_name,
            'contact_user_id': contact_user_id,
            'contact_vcard': contact_vcard,
            'media_group_id': media_group_id,
        }, **kwargs)


class TelegramFileResponse(Response):
    def __init__(self,
                 file_id: str,
                 file_path: str,
                 file_size: int,
                 *args, **kwargs):
        super().__init__(*args, output={
            'file_id': file_id,
            'file_path': file_path,
            'file_size': file_size,
        }, **kwargs)


class TelegramChatResponse(Response):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 chat_id: int,
                 link: str,
                 username: str,
                 invite_link: Optional[str],
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 type: Optional[str] = None,
                 first_name: Optional[str] = None,
                 last_name: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(*args, output={
            'chat_id': chat_id,
            'link': link,
            'invite_link': invite_link,
            'username': username,
            'title': title,
            'description': description,
            'type': type,
            'first_name': first_name,
            'last_name': last_name,
        }, **kwargs)


class TelegramUserResponse(Response):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 user_id: int,
                 username: str,
                 is_bot: bool,
                 first_name: str,
                 last_name: Optional[str] = None,
                 language_code: Optional[str] = None,
                 link: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(*args, output={
            'user_id': user_id,
            'username': username,
            'is_bot': is_bot,
            'link': link,
            'language_code': language_code,
            'first_name': first_name,
            'last_name': last_name,
        }, **kwargs)


class TelegramUsersResponse(Response):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 users: List[TelegramUserResponse],
                 *args, **kwargs):
        super().__init__(*args, output=[user.output for user in users], **kwargs)


# vim:sw=4:ts=4:et:
