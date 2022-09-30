from marshmallow import Schema, fields


class Mimic3Schema(Schema):
    pass


class Mimic3VoiceSchema(Mimic3Schema):
    key = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'description': 'Unique voice ID',
            'example': 'en_UK/apope_low',
        },
    )

    language = fields.String(
        required=True,
        dump_only=True,
        metadata={
            'example': 'en_UK',
        },
    )

    language_english = fields.String(
        metadata={
            'description': 'Name of the language (in English)',
        }
    )

    language_native = fields.String(
        metadata={
            'description': 'Name of the language (in the native language)',
        }
    )

    name = fields.String(
        metadata={
            'example': 'apope_low',
        }
    )

    sample_text = fields.String(
        metadata={
            'example': 'Some text',
        }
    )

    description = fields.String()
    aliases = fields.List(fields.String)
