from marshmallow import EXCLUDE, fields
from marshmallow.schema import Schema
from marshmallow.validate import OneOf

from platypush.schemas import StrippedString


class PiholeStatusSchema(Schema):
    """
    Schema for a Pi-hole status response.


    "output": {
      "server": "dns.fabiomanganiello.com",
      "status": "enabled",
      "ads_percentage": 6.7,
      "blocked": 37191,
      "cached": 361426,
      "domain_count": 1656690,
      "forwarded": 150187,
      "queries": 552076,
      "total_clients": 57,
      "total_queries": 552076,
      "unique_clients": 41,
      "unique_domains": 39348,
      "version": "5.18.2"
    },
    """

    class Meta:  # type: ignore
        """
        Exclude unknown fields.
        """

        unknown = EXCLUDE

    server = StrippedString(
        required=True,
        metadata={
            'description': 'Hostname or IP of the Pi-hole server',
            'example': '192.168.1.254',
        },
    )

    status = fields.String(
        required=True,
        validate=OneOf(['enabled', 'disabled']),
        metadata={
            'description': 'Status of the Pi-hole server',
            'example': 'enabled',
        },
    )

    ads_percentage = fields.Float(
        required=True,
        metadata={
            'description': 'Percentage of ads blocked by the Pi-hole server',
            'example': 6.7,
        },
    )

    blocked = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of blocked queries',
            'example': 37191,
        },
    )

    cached = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of cached queries',
            'example': 361426,
        },
    )

    domain_count = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of domains resolved the Pi-hole server',
            'example': 1656690,
        },
    )

    forwarded = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of forwarded queries',
            'example': 150187,
        },
    )

    queries = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of processed queries since the latest restart',
            'example': 552076,
        },
    )

    total_clients = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of connected clients',
            'example': 57,
        },
    )

    total_queries = fields.Integer(
        required=True,
        metadata={
            'description': 'Total number of queries processed by the Pi-hole server',
            'example': 552076,
        },
    )

    unique_clients = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of unique IP addresses connected to the Pi-hole server',
            'example': 41,
        },
    )

    unique_domains = fields.Integer(
        required=True,
        metadata={
            'description': 'Number of unique domains resolved by the Pi-hole server',
            'example': 39348,
        },
    )

    version = StrippedString(
        required=True,
        metadata={
            'description': 'Version of the Pi-hole server',
            'example': '5.18.2',
        },
    )
