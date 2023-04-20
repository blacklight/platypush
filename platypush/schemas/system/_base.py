from dataclasses import field

from marshmallow.validate import Range


def percent_field(**kwargs):
    """
    Field used to model percentage float fields between 0 and 1.
    """
    return field(
        default_factory=float,
        metadata={
            'validate': Range(min=0, max=1),
            **kwargs,
        },
    )
