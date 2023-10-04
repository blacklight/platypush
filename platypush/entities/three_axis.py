from typing import Iterable, Mapping, Optional, Union
from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import is_defined
from platypush.common.sensors import Numeric

from .sensors import RawSensor


if not is_defined('three_axis_sensor'):

    class ThreeAxisSensor(RawSensor):
        """
        An entity that measures a time duration.
        """

        __tablename__ = 'three_axis_sensor'

        id = Column(
            Integer, ForeignKey(RawSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __table_args__ = {'extend_existing': True}
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
