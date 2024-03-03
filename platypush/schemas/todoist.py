from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema

from platypush.schemas import DateTime


class TodoistUserSchema(Schema):
    """
    Todoist user schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    auto_reminder = fields.Int()
    avatar_big = fields.Url(
        metadata={
            "description": "The user's avatar URL.",
            "example": "https://example.com/user/100x100.png",
        },
    )

    avatar_medium = fields.Url(
        metadata={
            "description": "The user's avatar URL.",
            "example": "https://example.com/user/50x50.png",
        },
    )

    avatar_s640 = fields.Url(
        metadata={
            "description": "The user's avatar URL.",
            "example": "https://example.com/user/640x640.png",
        },
    )

    avatar_small = fields.Url(
        metadata={
            "description": "The user's avatar URL.",
            "example": "https://example.com/user/25x25.png",
        },
    )

    business_account_id = fields.Int(
        metadata={
            "description": "The user's business account ID.",
            "example": 123456,
        },
    )

    daily_goal = fields.Int(
        metadata={
            "description": "The user's daily goal.",
            "example": 100,
        },
    )

    date_format = fields.String(
        metadata={
            "description": "The user's date format.",
            "example": "dd-mm-yyyy",
        },
    )

    dateist_inline_disabled = fields.Bool()
    dateist_lang = fields.String(
        metadata={
            "description": "The user's dateist language.",
            "example": "en",
        },
    )

    days_off = fields.List(
        fields.Int(),
        metadata={
            "description": "The user's days off.",
            "example": [0, 6],
        },
    )

    default_reminder = fields.String()
    email = fields.Email(
        metadata={
            "description": "The user's email.",
            "example": "user@example.com",
        },
    )

    features = fields.Dict()
    full_name = fields.String(
        metadata={
            "description": "The user's full name.",
            "example": "John Doe",
        },
    )

    id = fields.Int(
        required=True,
        metadata={
            "description": "The user's unique identifier.",
            "example": 123456,
        },
    )

    image_id = fields.String()
    inbox_project = fields.Int(
        metadata={
            "description": "The user's inbox project ID.",
            "example": 123456,
        },
    )

    is_biz_admin = fields.Bool()
    is_premium = fields.Bool()
    join_date = DateTime()
    karma = fields.Float()
    karma_trend = fields.String()
    lang = fields.String(
        metadata={
            "description": "The user's language.",
            "example": "en",
        },
    )

    legacy_inbox_project = fields.Int()
    mobile_host = fields.String()
    mobile_number = fields.String()
    next_week = fields.Int()
    premium_until = DateTime()
    share_limit = fields.Int()
    sort_order = fields.Int()
    start_day = fields.Int()
    start_page = fields.String()
    theme = fields.Int()
    time_format = fields.String(
        metadata={
            "description": "The user's time format.",
            "example": "24h",
        },
    )

    token = fields.String()
    tz_info = fields.Dict()
    unique_prefix = fields.Int()
    websocket_url = fields.Url()
    weekly_goal = fields.Int()


class TodoistProjectSchema(Schema):
    """
    Todoist project schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    child_order = fields.Int()
    collapsed = fields.Bool()
    color = fields.Int()
    has_more_notes = fields.Bool()
    id = fields.Int(required=True)
    is_archived = fields.Bool()
    is_deleted = fields.Bool()
    is_favorite = fields.Bool()
    name = fields.String(required=True)
    shared = fields.Bool()
    inbox_project = fields.Bool()
    legacy_id = fields.Int()
    parent_id = fields.Int()


class TodoistItemSchema(Schema):
    """
    Todoist item schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    assigned_by_uid = fields.Int()
    checked = fields.Bool()
    child_order = fields.Int()
    collapsed = fields.Bool()
    content = fields.String()
    date_added = DateTime()
    date_completed = DateTime()
    day_order = fields.Int()
    due = fields.Dict()
    has_more_notes = fields.Bool()
    id = fields.Int(required=True)
    in_history = fields.Bool()
    is_deleted = fields.Bool()
    labels = fields.List(fields.String())
    legacy_project_id = fields.Int()
    parent_id = fields.Int()
    priority = fields.Int()
    project_id = fields.Int()
    responsible_uid = fields.Int()
    section_id = fields.Int()
    sync_id = fields.Int()
    user_id = fields.Int()


class TodoistFilterSchema(Schema):
    """
    Todoist filter schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    color = fields.Int()
    id = fields.Int(required=True)
    is_deleted = fields.Bool()
    item_order = fields.Int()
    name = fields.String()
    query = fields.String()
    user_id = fields.Int()


class TodoistLiveNotificationSchema(Schema):
    """
    Todoist live notifications schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    id = fields.Int(required=True)
    notification_key = fields.String()
    notification_type = fields.String()
    project_id = fields.Int()
    user_id = fields.Int()
    is_deleted = fields.Bool()
    is_unread = fields.Bool()
    completed_last_month = fields.Bool()
    karma_level = fields.Int()
    promo_img = fields.Url()
    completed_tasks = fields.Int()
    created = fields.String()


class TodoistCollaboratorSchema(Schema):
    """
    Todoist collaborator schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    data = fields.Dict()


class TodoistNoteSchema(Schema):
    """
    Todoist note schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    data = fields.Dict()


class TodoistProjectNoteSchema(Schema):
    """
    Todoist project note schema.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta class.
        """

        unknown = EXCLUDE

    data = fields.Dict()
