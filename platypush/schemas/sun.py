from marshmallow import fields
from marshmallow.schema import Schema


class SunEventsSchema(Schema):
    sunrise = fields.DateTime(metadata=dict(description='Next sunrise time'))
    sunset = fields.DateTime(metadata=dict(description='Next sunset time'))
    solar_noon = fields.DateTime(metadata=dict(description='Next solar noon time'))
    civil_twilight_begin = fields.DateTime(metadata=dict(description='Next civil twilight start time'))
    civil_twilight_end = fields.DateTime(metadata=dict(description='Next civil twilight end time'))
    nautical_twilight_begin = fields.DateTime(metadata=dict(description='Next nautical twilight start time'))
    nautical_twilight_end = fields.DateTime(metadata=dict(description='Next nautical twilight end time'))
    astronomical_twilight_begin = fields.DateTime(metadata=dict(description='Next astronomical twilight start time'))
    astronomical_twilight_end = fields.DateTime(metadata=dict(description='Next astronomical twilight end time'))
