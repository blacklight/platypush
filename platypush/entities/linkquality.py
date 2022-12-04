from sqlalchemy import Column, Integer, ForeignKey

from platypush.common.db import Base

from .sensors import NumericSensor


if 'link_quality' not in Base.metadata:

    class LinkQuality(NumericSensor):
        __tablename__ = 'link_quality'

        def __init__(
            self, *args, unit: str = '%', min: float = 0, max: float = 100, **kwargs
        ):
            super().__init__(*args, min=min, max=max, unit=unit, **kwargs)

        id = Column(
            Integer, ForeignKey(NumericSensor.id, ondelete='CASCADE'), primary_key=True
        )

        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
