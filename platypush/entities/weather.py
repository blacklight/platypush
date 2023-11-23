from sqlalchemy import JSON, Column, DateTime, Float, Integer, ForeignKey, String

from . import Entity


class Weather(Entity):
    """
    Weather entity.
    """

    __tablename__ = 'weather'

    id = Column(Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True)

    summary = Column(String)
    icon = Column(String)
    image = Column(String)
    precip_intensity = Column(Float)
    precip_type = Column(String)
    temperature = Column(Float)
    apparent_temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    rain_chance = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(String)
    wind_gust = Column(Float)
    cloud_cover = Column(Float)
    visibility = Column(Float)
    sunrise = Column(DateTime)
    sunset = Column(DateTime)
    units = Column(String)

    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }


class WeatherForecast(Entity):
    """
    Weather forecast entity.
    """

    __tablename__ = 'weather_forecast'

    id = Column(Integer, ForeignKey(Entity.id, ondelete='CASCADE'), primary_key=True)
    # forecast contains a list of serialized Weather entities
    forecast = Column(JSON)

    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
    }
