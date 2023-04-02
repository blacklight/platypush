from typing import Iterable, Mapping, Optional, Union
from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base
from platypush.common.sensors import Numeric

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

        @RawSensor.value.setter
        def value(
            self, value: Optional[Union[Iterable[Numeric], Mapping[str, Numeric]]]
        ):
            """
            Validates and normalizes the given value to a list of 3 numeric
            values.
            """
            if value is None:
                return

            if isinstance(value, dict):
                assert set(value.keys()) == {
                    'x',
                    'y',
                    'z',
                }, f'Invalid keys for entity of type {self.__class__}: "{value}"'

                value = [value[k] for k in ['x', 'y', 'z']]  # type: ignore

            assert (
                isinstance(value, (list, tuple))
                and len(value) == 3  # type: ignore
                and all(isinstance(v, (int, float)) for v in value)
            ), f'Invalid 3-axis value: {value}'

            super(ThreeAxisSensor, type(self)).value.fset(self, value)  # type: ignore
