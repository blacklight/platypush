from sqlalchemy import Column, Integer, ForeignKey

from .devices import entity_types_registry
from .sensors import NumericSensor


if not entity_types_registry.get('Battery'):

    class Battery(NumericSensor):
        __tablename__ = 'battery'

        def __init__(
            self,
            *args,
            value,
            unit: str = '%',
            min: float = 0,
            max: float = 100,
            **kwargs
        ):
            super().__init__(*args, **kwargs)
            self.value = float(value)
            self.unit = unit
            self.min = min
            self.max = max

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }

    entity_types_registry['Battery'] = Battery
else:
    Battery = entity_types_registry['Battery']
