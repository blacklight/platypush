from marshmallow import Schema, pre_dump
from marshmallow.fields import Boolean, Integer, Date, Float, String


class TelegramMessageSchema(Schema):
    """
    Schema for Telegram messages.
    """

    message_id = Integer(required=True)
    chat_id = Integer(required=True)
    creation_date = Date()
    chat_username = String()
    chat_firstname = String()
    chat_lastname = String()
    from_user_id = Integer()
    from_username = String()
    from_firstname = String()
    from_lastname = String()
    text = String()
    caption = String()
    edit_date = Date()
    forward_from_message_id = Integer()
    forward_date = Date()
    photo_file_id = String()
    photo_file_size = Integer()
    photo_width = Integer()
    photo_height = Integer()
    document_file_id = String()
    document_file_name = String()
    document_file_size = Integer()
    document_mime_type = String()
    audio_file_id = String()
    audio_file_size = Integer()
    audio_mime_type = String()
    audio_performer = String()
    audio_title = String()
    audio_duration = Integer()
    location_latitude = Float()
    location_longitude = Float()
    contact_phone_number = String()
    contact_first_name = String()
    contact_last_name = String()
    contact_user_id = Integer()
    contact_vcard = String()
    video_file_id = String()
    video_file_size = Integer()
    video_width = Integer()
    video_height = Integer()
    video_mime_type = String()
    video_duration = Integer()
    link = String()
    media_group_id = String()

    @pre_dump
    def pre_dump(self, msg, **_) -> dict:
        ret = {
            'message_id': msg.message_id,
            'chat_id': msg.chat_id,
            'chat_username': msg.chat.username,
            'chat_firstname': msg.chat.first_name,
            'chat_lastname': msg.chat.last_name,
            'text': msg.text,
            'caption': msg.caption,
            'creation_date': msg.date,
            'edit_date': msg.edit_date,
            'forward_date': msg.forward_date,
            'forward_from_message_id': msg.forward_from_message_id,
            'link': msg.link,
            'media_group_id': msg.media_group_id,
        }

        if msg.from_user:
            ret.update(
                {
                    'from_user_id': msg.from_user.id,
                    'from_username': msg.from_user.username,
                    'from_firstname': msg.from_user.first_name,
                    'from_lastname': msg.from_user.last_name,
                }
            )

        if msg.photo:
            ret.update(
                {
                    'photo_file_id': msg.photo[-1].file_id,
                    'photo_file_size': msg.photo[-1].file_size,
                    'photo_width': msg.photo[-1].width,
                    'photo_height': msg.photo[-1].height,
                }
            )

        if msg.document:
            ret.update(
                {
                    'document_file_id': msg.document.file_id,
                    'document_file_name': msg.document.file_name,
                    'document_file_size': msg.document.file_size,
                    'document_mime_type': msg.document.mime_type,
                }
            )

        if msg.audio:
            ret.update(
                {
                    'audio_file_id': msg.audio.file_id,
                    'audio_file_size': msg.audio.file_size,
                    'audio_mime_type': msg.audio.mime_type,
                    'audio_performer': msg.audio.performer,
                    'audio_title': msg.audio.title,
                    'audio_duration': msg.audio.duration,
                }
            )

        if msg.video:
            ret.update(
                {
                    'video_file_id': msg.video.file_id,
                    'video_file_size': msg.video.file_size,
                    'video_width': msg.video.width,
                    'video_height': msg.video.height,
                    'video_mime_type': msg.video.mime_type,
                    'video_duration': msg.video.duration,
                }
            )

        if msg.location:
            ret.update(
                {
                    'location_latitude': msg.location.latitude,
                    'location_longitude': msg.location.longitude,
                }
            )

        if msg.contact:
            ret.update(
                {
                    'contact_phone_number': msg.contact.phone_number,
                    'contact_first_name': msg.contact.first_name,
                    'contact_last_name': msg.contact.last_name,
                    'contact_user_id': msg.contact.user_id,
                    'contact_vcard': msg.contact.vcard,
                }
            )

        return ret


class TelegramFileSchema(Schema):
    """
    Schema for Telegram files.
    """

    file_id = String(required=True)
    file_path = String(required=True)
    file_size = Integer(required=True)


class TelegramUserSchema(Schema):
    """
    Schema for Telegram users.
    """

    user_id = Integer(required=True, data_key='id')
    username = String(required=True)
    is_bot = Boolean(required=True)
    first_name = String(required=True)
    last_name = String()
    language_code = String()
    link = String()


class TelegramChatSchema(Schema):
    """
    Schema for Telegram chats.
    """

    chat_id = Integer(required=True)
    link = String(required=True)
    username = String(required=True)
    invite_link = String()
    title = String()
    description = String()
    type = String()
    first_name = String()
    last_name = String()
