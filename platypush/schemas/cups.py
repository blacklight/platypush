from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema


class PrinterSchema(Schema):
    """
    Schema for the printers returned by the CUPS API.
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    name = fields.String(
        required=True,
        metadata={
            'description': 'The name of the printer.',
            'example': 'HP_DeskJet_5820_series_585C26',
        },
    )

    printer_type = fields.String(
        required=True,
        data_key='printer-type',
        metadata={
            'description': 'Unique type ID of the printer.',
            'example': 2101260,
        },
    )

    info = fields.String(
        required=True,
        data_key='printer-info',
        metadata={
            'description': 'Human-readable description of the printer.',
            'example': 'HP DeskJet 5820 series',
        },
    )

    uri = fields.String(
        required=True,
        data_key='device-uri',
        metadata={
            'description': 'The URI of the printer.',
            'example': (
                'dnssd://HP%20DeskJet%205820%20series%20%5B585C26%5D._ipp._tcp.local/'
                '?uuid=1c852a4d-b800-1f08-abcd-705a0f585c26'
            ),
        },
    )

    state = fields.String(
        required=True,
        data_key='printer-state',
        metadata={
            'description': 'The state of the printer.',
            'example': 3,
        },
    )

    is_shared = fields.Boolean(
        required=True,
        data_key='printer-is-shared',
        metadata={
            'description': 'Whether the printer is shared.',
            'example': False,
        },
    )

    state_message = fields.String(
        required=True,
        data_key='printer-state-message',
        metadata={
            'description': 'The state message of the printer.',
            'example': 'Idle',
        },
    )

    state_reasons = fields.List(
        fields.String(),
        required=True,
        data_key='printer-state-reasons',
        metadata={
            'description': 'The reasons for the printer state.',
            'example': ['none'],
        },
    )

    location = fields.String(
        required=True,
        data_key='printer-location',
        metadata={
            'description': 'Human-readable location of the printer.',
            'example': 'Living Room',
        },
    )

    uri_supported = fields.String(
        required=True,
        data_key='printer-uri-supported',
        metadata={
            'description': 'The URI of the printer exposed by the CUPS server.',
            'example': 'ipp://localhost:631/printers/HP_OfficeJet_5230',
        },
    )

    make_and_model = fields.String(
        required=True,
        data_key='printer-make-and-model',
        metadata={
            'description': 'The make and model of the printer.',
            'example': 'HP Officejet 5200 Series, hpcups 3.19.1',
        },
    )


class JobAddedSchema(Schema):
    """
    Schema for a printer job added event.
    """

    printer = fields.String(
        required=True,
        metadata={
            'description': 'The name of the printer.',
            'example': 'HP_DeskJet_5820_series_585C26',
        },
    )

    job_id = fields.Integer(
        required=True,
        data_key='job-id',
        metadata={
            'description': 'The ID of the job.',
            'example': 1,
        },
    )
