import json

from marshmallow import EXCLUDE, fields, pre_dump
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class PushbulletActionSchema(Schema):
    """
    Schema for Pushbullet notification actions.
    """

    label = fields.String(
        required=True,
        metadata={
            'description': 'Label of the action',
            'example': 'Example action',
        },
    )

    trigger_key = fields.String(
        required=True,
        metadata={
            'description': 'Key of the action',
            'example': 'example_action',
        },
    )


class PushbulletSchema(Schema):
    """
    Schema for Pushbullet API messages.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    notification_id = fields.String(
        required=True,
        metadata={
            'description': 'Unique identifier for the notification/message',
            'example': '12345',
        },
    )

    title = fields.String(
        metadata={
            'description': 'Title of the notification/message',
            'example': 'Hello world',
        },
    )

    body = fields.Raw(
        metadata={
            'description': 'Body of the notification/message',
            'example': 'Example body',
        },
    )

    url = fields.Url(
        metadata={
            'description': 'URL attached to the notification/message',
            'example': 'https://example.com',
        },
    )

    source_user = fields.String(
        attribute='source_user_iden',
        metadata={
            'description': 'Source user of the notification/message',
            'example': 'user123',
        },
    )

    source_device = fields.String(
        attribute='source_device_iden',
        metadata={
            'description': 'Source device of the notification/message',
            'example': 'device123',
        },
    )

    target_device = fields.String(
        attribute='target_device_iden',
        metadata={
            'description': 'Target device of the notification/message',
            'example': 'device456',
        },
    )

    sender_id = fields.String(
        attribute='sender_iden',
        metadata={
            'description': 'Sender ID of the notification/message',
            'example': '12345',
        },
    )

    sender_email = fields.Email(
        attribute='sender_email_normalized',
        metadata={
            'description': 'Sender email of the notification/message',
            'example': 'user1@example.com',
        },
    )

    sender_name = fields.String(
        metadata={
            'description': 'Sender name of the notification/message',
            'example': 'John Doe',
        },
    )

    receiver_id = fields.String(
        attribute='receiver_iden',
        metadata={
            'description': 'Receiver ID of the notification/message',
            'example': '12346',
        },
    )

    receiver_email = fields.Email(
        attribute='receiver_email_normalized',
        metadata={
            'description': 'Receiver email of the notification/message',
            'example': 'user2@example.com',
        },
    )

    dismissible = fields.Boolean(
        metadata={
            'description': 'Whether the notification/message is dismissible',
            'example': True,
        },
    )

    icon = fields.String(
        metadata={
            'description': 'Base64 encoded icon of the notification/message',
            'example': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABpUlEQVQ4T',
        },
    )

    application_name = fields.String(
        metadata={
            'description': 'Name of the application that sent the notification/message',
            'example': 'Example app',
        },
    )

    package_name = fields.String(
        metadata={
            'description': 'Package name of the application that sent the notification/message',
            'example': 'com.example.app',
        },
    )

    file_name = fields.String(
        metadata={
            'description': 'Name of the file attached to the notification/message',
            'example': 'example.txt',
        },
    )

    file_type = fields.String(
        metadata={
            'description': 'Type of the file attached to the notification/message',
            'example': 'text/plain',
        },
    )

    file_url = fields.Url(
        metadata={
            'description': 'URL of the file attached to the notification/message',
            'example': 'https://example.com/example.txt',
        },
    )

    image_width = fields.Integer(
        metadata={
            'description': 'Width of the image attached to the notification/message',
            'example': 100,
        },
    )

    image_height = fields.Integer(
        metadata={
            'description': 'Height of the image attached to the notification/message',
            'example': 100,
        },
    )

    image_url = fields.Url(
        metadata={
            'description': 'URL of the image attached to the notification/message',
            'example': 'https://example.com/example.png',
        },
    )

    actions = fields.Nested(
        PushbulletActionSchema,
        many=True,
        metadata={
            'description': 'Actions of the notification/message',
        },
    )

    created = DateTime(
        metadata={
            'description': 'Creation timestamp of the notification/message',
            'example': '2021-01-01T00:00:00',
        },
    )

    modified = DateTime(
        metadata={
            'description': 'Last modification timestamp of the notification/message',
            'example': '2021-01-01T00:00:00',
        },
    )

    @pre_dump
    def pre_dump(self, data, **_):
        """
        Pre-dump hook.
        """

        data['notification_id'] = str(
            data.pop('iden', data.pop('notification_id', None))
        )

        if data.get('body') is not None:
            try:
                data['body'] = json.loads(data['body'])
            except (TypeError, ValueError):
                pass

        return data


class PushbulletDeviceSchema(Schema):
    """
    Schema for Pushbullet devices.
    """

    active = fields.Boolean(
        metadata={
            'description': 'Whether the device is active',
            'example': True,
        },
    )

    device_id = fields.String(
        required=True,
        attribute='iden',
        metadata={
            'description': 'Unique identifier for the device',
            'example': '12345',
        },
    )

    name = fields.String(
        attribute='nickname',
        metadata={
            'description': 'Name of the device',
            'example': 'Example device',
        },
    )

    kind = fields.String(
        metadata={
            'description': 'Kind of the device',
            'example': 'android',
        },
    )

    manufacturer = fields.String(
        metadata={
            'description': 'Manufacturer of the device',
            'example': 'Example manufacturer',
        },
    )

    model = fields.String(
        metadata={
            'description': 'Model of the device',
            'example': 'Example model',
        },
    )

    icon = fields.String(
        metadata={
            'description': 'Device icon type',
            'example': 'system',
        },
    )

    pushable = fields.Boolean(
        metadata={
            'description': 'Whether it is possible to push notifications and '
            'messages to the device',
            'example': True,
        },
    )

    created = DateTime(
        metadata={
            'description': 'Creation timestamp of the device',
            'example': '2021-01-01T00:00:00',
        },
    )

    modified = DateTime(
        metadata={
            'description': 'Last modification timestamp of the device',
            'example': '2021-01-01T00:00:00',
        },
    )
