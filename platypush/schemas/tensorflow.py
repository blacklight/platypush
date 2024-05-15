from marshmallow import fields
from marshmallow.schema import Schema

from platypush.schemas import StrippedString


class TensorflowTrainSchema(Schema):
    """
    Schema for TensorFlow model training results.
    """

    model = StrippedString(
        required=True,
        metadata={
            "description": "Model name.",
            "example": "MyModel",
        },
    )

    epochs = fields.Int(
        required=True,
        metadata={
            "description": "Number of epochs.",
            "example": 10,
        },
    )

    history = fields.Dict(
        metadata={
            "description": "Training history.",
            "example": {
                "loss": [0.1, 0.2, 0.3],
                "accuracy": [0.9, 0.8, 0.7],
            },
        },
    )
