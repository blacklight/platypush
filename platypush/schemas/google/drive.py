from marshmallow import INCLUDE, fields, pre_dump
from marshmallow.schema import Schema


class GoogleDriveFileSchema(Schema):
    """
    Schema for Google Drive files.
    """

    class Meta:  # type: ignore
        """
        Include unknown fields in the deserialized output.
        """

        unknown = INCLUDE

    id = fields.String(
        required=True,
        metadata={'description': 'File ID'},
    )

    type = fields.String(
        required=True,
        metadata={
            'description': 'File type',
            'example': 'file',
        },
    )

    name = fields.String(
        required=True,
        metadata={'description': 'File name'},
    )

    mime_type = fields.String(
        required=True,
        metadata={
            'description': 'File MIME type',
            'example': 'plain/text',
        },
    )

    @pre_dump
    def parse_type(self, data, **_):
        data['type'] = data.pop('kind').split('#')[-1]
        data['mime_type'] = data.pop('mimeType')
        return data
