from marshmallow import fields
from marshmallow.schema import Schema

from platypush.plugins.media import DownloadState
from platypush.schemas import DateTime


class MediaDownloadSchema(Schema):
    """
    Media download schema.
    """

    url = fields.URL(
        required=True,
        metadata={
            "description": "Download URL",
            "example": "https://example.com/video.mp4",
        },
    )

    path = fields.String(
        required=True,
        metadata={
            "description": "Download path",
            "example": "/path/to/download/video.mp4",
        },
    )

    state = fields.Enum(
        DownloadState,
        required=True,
        metadata={
            "description": "Download state",
        },
    )

    size = fields.Integer(
        nullable=True,
        metadata={
            "description": "Download size (bytes)",
            "example": 1024,
        },
    )

    timeout = fields.Integer(
        nullable=True,
        metadata={
            "description": "Download timeout (seconds)",
            "example": 60,
        },
    )

    started_at = DateTime(
        nullable=True,
        metadata={
            "description": "Download start time",
        },
    )

    ended_at = DateTime(
        nullable=True,
        metadata={
            "description": "Download end time",
        },
    )
