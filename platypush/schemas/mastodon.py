from random import randint

from marshmallow import fields, missing
from marshmallow.schema import Schema
from marshmallow.validate import OneOf

from platypush.schemas import DateTime, Date, StrippedString

notification_types = ['follow', 'favourite', 'reblog', 'mention', 'poll', 'follow_request']
list_reply_policies = ['none', 'followed', 'list']


class MastodonSchema(Schema):
    pass


class MastodonAccountSchema(MastodonSchema):
    id = fields.String(
        dump_only=True,
        metadata=dict(
            example=''.join([f'{randint(1, 9)}' for _ in range(18)]),
        )
    )

    username = fields.String(
        metadata=dict(
            example='admin',
        )
    )

    url = fields.URL()
    avatar = fields.URL()
    header = fields.URL()
    followers_count = fields.Int(dump_only=True)
    following_count = fields.Int(dump_only=True)
    note = fields.String()
    display_name = StrippedString(
        metadata=dict(
            example='Name Surname',
        )
    )

    locked = fields.Boolean()
    bot = fields.Boolean()
    discoverable = fields.Boolean()
    group = fields.Boolean()
    created_at = DateTime(dump_only=True)
    last_status_at = DateTime(dump_only=True)


class MastodonFeaturedHashtagSchema(MastodonSchema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    statuses_count = fields.Int(dump_only=True)
    last_status = DateTime(dump_only=True)


class MastodonHashtagHistorySchema(MastodonSchema):
    day = Date()
    uses = fields.Int()
    accounts = fields.Int()


class MastodonHashtagSchema(MastodonSchema):
    name = fields.String(metadata=dict(example='hashtag'))
    url = fields.URL()
    history = fields.Nested(
        MastodonHashtagHistorySchema, many=True, default=missing
    )


class MastodonMediaSchema(MastodonSchema):
    id = fields.String(dump_only=True)
    description = StrippedString()
    type = fields.String(dump_only=True, metadata={'example': 'image'})
    url = fields.URL(dump_only=True)
    preview_url = fields.URL(dump_only=True)
    remote_url = fields.URL(dump_only=True)
    preview_remote_url = fields.URL(dump_only=True)
    meta = fields.Dict()


class MastodonStatusSchema(MastodonSchema):
    id = fields.String(
        dump_only=True,
        metadata=dict(
            example=''.join([f'{randint(1, 9)}' for _ in range(18)]),
        )
    )

    in_reply_to_id = fields.String(
        dump_only=True,
        allow_none=True,
        metadata=dict(
            example=''.join([f'{randint(1, 9)}' for _ in range(18)]),
        )
    )

    in_reply_to_account_id = fields.String(
        dump_only=True,
        allow_none=True,
        metadata=dict(
            example=''.join([f'{randint(1, 9)}' for _ in range(18)]),
        )
    )

    url = fields.URL(dump_only=True)
    content = fields.String(allow_none=False)
    account = fields.Nested(MastodonAccountSchema, dump_only=True)
    attachments = fields.Nested(
        MastodonMediaSchema,
        many=True,
        dump_only=True,
        attribute='media_attachments',
    )
    hashtags = fields.Nested(
        MastodonHashtagSchema, many=True,
        attribute='tags', dump_only=True
    )

    replies_count = fields.Int(dump_only=True)
    reblogs_count = fields.Int(dump_only=True)
    favourites_count = fields.Int(dump_only=True)

    sensitive = fields.Boolean()
    favourited = fields.Boolean()
    reblogged = fields.Boolean()
    muted = fields.Boolean()
    bookmarked = fields.Boolean()
    pinned = fields.Boolean()

    created_at = DateTime(dump_only=True)


class MastodonSearchSchema(MastodonSchema):
    accounts = fields.Nested(MastodonAccountSchema, many=True)
    statuses = fields.Nested(MastodonStatusSchema, many=True)
    hashtags = fields.Nested(MastodonHashtagSchema, many=True)


class MastodonAccountCreationSchema(MastodonSchema):
    access_token = fields.String(dump_only=True)
    token_type = fields.String(dump_only=True, metadata={'example': 'Bearer'})
    scope = fields.String(dump_only=True, metadata={'example': 'read write follow push'})
    created_at = DateTime(dump_only=True)


class MastodonAccountListSchema(MastodonSchema):
    id = fields.Int(dump_only=True)
    title = StrippedString()


class MastodonFilterSchema(MastodonSchema):
    id = fields.Int(dump_only=True)
    phrase = StrippedString()
    whole_word = fields.Boolean()
    irreversible = fields.Boolean()
    expires_at = DateTime(allow_none=True)
    context = fields.List(
        fields.String(validate=OneOf(['home', 'notifications', 'public', 'thread'])),
        metadata={
            'example': 'Which context(s) this filter applies to. '
                       'Possible values: home, notifications, public, thread',
        }
    )


class MastodonConversationSchema(MastodonSchema):
    id = fields.Int(dump_only=True)
    unread = fields.Boolean()
    accounts = fields.Nested(MastodonAccountSchema, many=True)
    last_status = fields.Nested(MastodonStatusSchema)


class MastodonListSchema(MastodonSchema):
    id = fields.Int(dump_only=True)
    title = StrippedString()
    replies_policy = fields.String(validate=OneOf(list_reply_policies))


class MastodonMentionSchema(MastodonSchema):
    id = fields.Int(dump_only=True)
    username = StrippedString(metadata=dict(example='user'))
    url = fields.URL(metadata=dict(example='https://mastodon.social/@user'))


class MastodonNotificationSchema(MastodonSchema):
    id = fields.String(dump_only=True)
    type = fields.String(validate=OneOf(notification_types))
    account = fields.Nested(MastodonAccountSchema)
    status = fields.Nested(MastodonStatusSchema)
    mention = fields.Nested(MastodonMentionSchema)
    created_at = DateTime(dump_only=True)


class MastodonSubscriptionNotificationTypes(MastodonSchema):
    follow = fields.Boolean()
    reblog = fields.Boolean()
    mention = fields.Boolean()
    favourite = fields.Boolean()
    poll = fields.Boolean()
