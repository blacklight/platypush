import base64

from marshmallow import EXCLUDE, fields, pre_dump
from marshmallow.schema import Schema


class QrcodeGeneratedSchema(Schema):
    """
    Schema for a QR code generation response.
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    text = fields.String(
        required=True,
        metadata={
            'description': 'Text content of the QR code, or base64-encoded binary data',
            'example': 'https://platypush.tech',
        },
    )

    data = fields.String(
        metadata={
            'description': 'Base64-encoded content of the QR code',
            'example': 'iVBORw0KGgoAAAANSUhEUgAAAXIAAAFyAQAAAADAX2yk',
        }
    )

    format = fields.String(
        metadata={
            'description': 'Format of the QR code image',
            'example': 'png',
        },
    )

    image_file = fields.String(
        metadata={
            'description': 'Path to the generated QR code image file',
            'example': '/tmp/qr_code.png',
        },
    )


class QrcodeDecodedRectSchema(Schema):
    """
    Schema for a single QR code decoding result rectangle.
    """

    x = fields.Integer(
        required=True,
        metadata={
            'description': 'X coordinate of the rectangle in the image',
            'example': 0,
        },
    )

    y = fields.Integer(
        required=True,
        metadata={
            'description': 'Y coordinate of the rectangle in the image',
            'example': 0,
        },
    )

    width = fields.Integer(
        required=True,
        metadata={
            'description': 'Width of the rectangle',
            'example': 100,
        },
    )

    height = fields.Integer(
        required=True,
        metadata={
            'description': 'Height of the rectangle',
            'example': 100,
        },
    )


class QrcodeDecodedResultSchema(Schema):
    """
    Schema for a single QR code decoding result.
    """

    data = fields.String(
        required=True,
        metadata={
            'description': 'Decoded QRcode data, as a base64-encoded string if binary',
            'example': 'https://platypush.tech',
        },
    )

    type = fields.String(
        required=True,
        metadata={
            'description': (
                'Type of code that was decoded. Supports the types available under the '
                '`pyzbar.ZBarSymbol` class: '
                'https://github.com/NaturalHistoryMuseum/pyzbar/blob/master/pyzbar/wrapper.py#L43'
            ),
            'example': 'QRCODE',
        },
    )

    rect = fields.Nested(
        QrcodeDecodedRectSchema,
        required=True,
        metadata={
            'description': 'Rectangle in the image where the QR code was found',
        },
    )

    @pre_dump
    def pre_dump(self, data, **_):
        if hasattr(data, '_asdict'):
            data = data._asdict()

        try:
            data['data'] = data['data'].decode()
        except (ValueError, TypeError):
            data['data'] = base64.b64encode(data['data']).decode()

        return data


class QrcodeDecodedSchema(Schema):
    """
    Schema for a QR code decoding response.
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    results = fields.List(
        fields.Nested(QrcodeDecodedResultSchema),
        required=True,
        metadata={
            'description': 'Decoded QR code results',
        },
    )

    image_file = fields.String(
        metadata={
            'description': 'Path to the image file that was decoded',
            'example': '/tmp/qr_code.png',
        },
    )
