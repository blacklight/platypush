from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import reconstructor, validates

from platypush.common.db import Base

from .sensors import RawSensor


if 'three_axis_sensor' not in Base.metadata:

    class ThreeAxisSensor(RawSensor):
        """
        An entity that measures a time duration.
        """

        __tablename__ = 'three_axis_sensor'

        id = Column(
            Integer, ForeignKey(RawSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

        @validates('_value')
        def check_value(self, _, value):
            assert (
                isinstance('_value', (list, tuple))
                and len(value) == 3
                and all(isinstance(v, (int, float)) for v in value)
            ), f'Invalid 3-axis value: {value}'

            return list(value)

        @reconstructor
        def post_init(self):
            self.is_json = True
