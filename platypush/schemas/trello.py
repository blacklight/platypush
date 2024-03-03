from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema


class TrelloLabelSchema(Schema):
    """
    Trello label schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The label's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        required=True,
        metadata={
            "description": "The label's name.",
            "example": "My Label",
        },
    )

    color = fields.String(
        metadata={
            "description": "The label's color.",
            "example": "green",
        },
    )


class TrelloUserSchema(Schema):
    """
    Trello user schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The user's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    username = fields.String(
        required=True,
        metadata={
            "description": "The user's username.",
            "example": "myusername",
        },
    )

    fullname = fields.String(
        metadata={
            "description": "The user's full name.",
            "example": "My Full Name",
        },
    )

    initials = fields.String(
        metadata={
            "description": "The user's initials.",
            "example": "MFN",
        },
    )

    avatar_url = fields.Url(
        metadata={
            "description": "The user's avatar URL.",
            "example": "https://trello-avatars.s3.amazonaws.com/5d62808da5d6a95a3a3e4f2f/50.png",
        },
    )


class TrelloMemberSchema(Schema):
    """
    Trello member schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The user's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    username = fields.String(
        required=True,
        metadata={
            "description": "The user's username.",
            "example": "myusername",
        },
    )

    fullname = fields.String(
        metadata={
            "description": "The user's full name.",
            "example": "My Full Name",
        },
    )

    initials = fields.String(
        metadata={
            "description": "The user's initials.",
            "example": "MFN",
        },
    )

    bio = fields.String(
        metadata={
            "description": "The user's bio.",
            "example": "My bio.",
        },
    )

    member_type = fields.String(
        metadata={
            "description": "The user's type.",
            "example": "admin",
        },
    )


class TrelloCommentSchema(Schema):
    """
    Trello comment schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The comment's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    text = fields.String(
        required=True,
        metadata={
            "description": "The comment's text.",
            "example": "My comment's text.",
        },
    )

    type = fields.String(
        required=True,
        metadata={
            "description": "The comment's type.",
            "example": "commentCard",
        },
    )

    creator = fields.Nested(TrelloUserSchema)
    date = fields.DateTime(
        metadata={
            "description": "The comment's date.",
            "example": "2019-08-25T15:32:13.000Z",
        },
    )


class TrelloListSchema(Schema):
    """
    Trello list schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    id = fields.String(
        required=True,
        metadata={
            "description": "The list's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        required=True,
        metadata={
            "description": "The list's name.",
            "example": "My List",
        },
    )

    closed = fields.Boolean(
        missing=False,
        metadata={
            "description": "Whether the list is closed.",
            "example": False,
        },
    )

    subscribed = fields.Boolean(
        missing=False,
        metadata={
            "description": "Whether the list is subscribed.",
            "example": False,
        },
    )


class TrelloBoardSchema(Schema):
    """
    Trello board schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    id = fields.String(
        required=True,
        metadata={
            "description": "The board's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        required=True,
        metadata={
            "description": "The board's name.",
            "example": "My Board",
        },
    )

    url = fields.Url(
        required=True,
        metadata={
            "description": "The board's URL.",
            "example": "https://trello.com/b/5d62808da5d6a95a3a3e4f2f/my-board",
        },
    )

    closed = fields.Boolean(
        missing=False,
        metadata={
            "description": "Whether the board is closed.",
            "example": False,
        },
    )

    lists = fields.Nested(
        TrelloListSchema,
        many=True,
        metadata={
            "description": "The board's lists.",
        },
    )

    date_last_activity = fields.DateTime(
        metadata={
            "description": "The board's last activity date.",
            "example": "2019-08-25T15:52:45.000Z",
        },
    )


class TrelloPreviewSchema(Schema):
    """
    Trello attachment preview schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The preview's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    url = fields.Url(
        required=True,
        metadata={
            "description": "The preview's URL.",
            "example": "https://trello.com/c/5d62808da5d6a95a3a3e4f2f/my-attachment-txt.jpg",
        },
    )

    scaled = fields.Boolean(
        metadata={
            "description": "Whether the preview is scaled.",
            "example": True,
        },
    )

    size = fields.Integer(
        metadata={
            "description": "The preview's size, in bytes.",
            "example": 10000,
        },
    )

    width = fields.Integer(
        metadata={
            "description": "The preview's width, in pixels.",
            "example": 100,
        },
    )

    height = fields.Integer(
        metadata={
            "description": "The preview's height, in pixels.",
            "example": 100,
        },
    )


class TrelloChecklistItemSchema(Schema):
    """
    Trello checklist item schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The checklist item's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        required=True,
        metadata={
            "description": "The checklist item's name.",
            "example": "My Checklist Item",
        },
    )

    checked = fields.Boolean(
        metadata={
            "description": "Whether the checklist item is checked.",
            "example": True,
        },
    )


class TrelloChecklistSchema(Schema):
    """
    Trello checklist schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The checklist's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        metadata={
            "description": "The checklist's name.",
            "example": "My Checklist",
        },
    )

    items = fields.Nested(TrelloChecklistItemSchema, many=True)


class TrelloAttachmentSchema(Schema):
    """
    Trello attachment schema.
    """

    id = fields.String(
        required=True,
        metadata={
            "description": "The attachment's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        required=True,
        metadata={
            "description": "The attachment's name.",
            "example": "My Attachment.txt",
        },
    )

    url = fields.Url(
        required=True,
        metadata={
            "description": "The attachment's URL.",
            "example": "https://trello.com/c/5d62808da5d6a95a3a3e4f2f/my-attachment.txt",
        },
    )

    size = fields.Integer(
        metadata={
            "description": "The attachment's size, in bytes.",
            "example": 1024,
        },
    )

    date = fields.DateTime(
        metadata={
            "description": "The attachment's date.",
            "example": "2019-08-25T15:32:13.000Z",
        },
    )

    edge_color = fields.String(
        metadata={
            "description": "The attachment's edge color.",
            "example": "#000000",
        },
    )

    member_id = fields.String(
        metadata={
            "description": "The ID of the member who created the attachment.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    is_upload = fields.Boolean(
        metadata={
            "description": "Whether the attachment is an upload.",
            "example": True,
        },
    )

    mime_type = fields.String(
        metadata={
            "description": "The attachment's MIME type.",
            "example": "text/plain",
        },
    )

    previews = fields.Nested(TrelloPreviewSchema, many=True)


class TrelloCardSchema(Schema):
    """
    Trello card schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    id = fields.String(
        required=True,
        metadata={
            "description": "The card's unique identifier.",
            "example": "5d62808da5d6a95a3a3e4f2f",
        },
    )

    name = fields.String(
        required=True,
        metadata={
            "description": "The card's name.",
            "example": "My Card",
        },
    )

    description = fields.String(
        metadata={
            "description": "The card's description.",
            "example": "My card's description.",
        },
    )

    url = fields.Url(
        required=True,
        metadata={
            "description": "The card's URL.",
            "example": "https://trello.com/c/5d62808da5d6a95a3a3e4f2f/my-card",
        },
    )

    due_date = fields.DateTime(
        metadata={
            "description": "The card's due date.",
            "example": "2019-08-25T15:52:45.000Z",
        },
    )

    latest_card_move_date = fields.DateTime(
        metadata={
            "description": "The card's latest move date.",
            "example": "2019-08-25T15:52:45.000Z",
        },
    )

    date_last_activity = fields.DateTime(
        metadata={
            "description": "The card's last activity date.",
            "example": "2019-08-25T15:52:45.000Z",
        },
    )

    closed = fields.Boolean(
        missing=False,
        metadata={
            "description": "Whether the card is closed.",
            "example": False,
        },
    )

    is_due_complete = fields.Boolean(
        metadata={
            "description": "Whether the card is due complete.",
            "example": False,
        },
    )

    board = fields.Nested(TrelloBoardSchema)
    list = fields.Nested(TrelloListSchema)
    comments = fields.Nested(TrelloCommentSchema, many=True)
    labels = fields.Nested(TrelloLabelSchema, many=True)
    attachments = fields.Nested(TrelloAttachmentSchema, many=True)
    checklists = fields.Nested(TrelloChecklistSchema, many=True)
