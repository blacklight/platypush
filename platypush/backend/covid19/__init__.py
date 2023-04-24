import datetime
import os
from typing import Optional, Union, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session

from platypush.backend import Backend
from platypush.common.db import declarative_base
from platypush.config import Config
from platypush.context import get_plugin
from platypush.message.event.covid19 import Covid19UpdateEvent
from platypush.plugins.covid19 import Covid19Plugin

Base = declarative_base()
Session = scoped_session(sessionmaker())


class Covid19Update(Base):
    """Models the Covid19Data table"""

    __tablename__ = 'covid19data'
    __table_args__ = {'sqlite_autoincrement': True}

    country = Column(String, primary_key=True)
    confirmed = Column(Integer, nullable=False, default=0)
    deaths = Column(Integer, nullable=False, default=0)
    recovered = Column(Integer, nullable=False, default=0)
    last_updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class Covid19Backend(Backend):
    """
    This backend polls new data about the Covid-19 pandemic diffusion and triggers events when new data is available.

    Triggers:

        - :class:`platypush.message.event.covid19.Covid19UpdateEvent` when new data is available.

    """

    # noinspection PyProtectedMember
    def __init__(
        self,
        country: Optional[Union[str, List[str]]],
        poll_seconds: Optional[float] = 3600.0,
        **kwargs
    ):
        """
        :param country: Default country (or list of countries) to retrieve the stats for. It can either be the full
            country name or the country code. Special values:

            - ``world``: Get worldwide stats.
            - ``all``: Get all the available stats.

        Default: either the default configured on the :class:`platypush.plugins.covid19.Covid19Plugin` plugin or
        ``world``.

        :param poll_seconds: How often the backend should check for new check-ins (default: one hour).
        """
        super().__init__(poll_seconds=poll_seconds, **kwargs)
        self._plugin: Covid19Plugin = get_plugin('covid19')
        self.country: List[str] = self._plugin._get_countries(country)
        self.workdir = os.path.join(
            os.path.expanduser(Config.get('workdir')), 'covid19'
        )
        self.dbfile = os.path.join(self.workdir, 'data.db')
        os.makedirs(self.workdir, exist_ok=True)

    def __enter__(self):
        self.logger.info('Started Covid19 backend')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info('Stopped Covid19 backend')

    def _process_update(self, summary: Dict[str, Any], session: Session):
        update_time = datetime.datetime.fromisoformat(
            summary['Date'].replace('Z', '+00:00')
        )

        self.bus.post(
            Covid19UpdateEvent(
                country=summary['Country'],
                country_code=summary['CountryCode'],
                confirmed=summary['TotalConfirmed'],
                deaths=summary['TotalDeaths'],
                recovered=summary['TotalRecovered'],
                update_time=update_time,
            )
        )

        session.merge(
            Covid19Update(
                country=summary['CountryCode'],
                confirmed=summary['TotalConfirmed'],
                deaths=summary['TotalDeaths'],
                recovered=summary['TotalRecovered'],
                last_updated_at=update_time,
            )
        )

    def loop(self):
        # noinspection PyUnresolvedReferences
        summaries = self._plugin.summary(self.country).output
        if not summaries:
            return

        engine = create_engine(
            'sqlite:///{}'.format(self.dbfile),
            connect_args={'check_same_thread': False},
        )
        Base.metadata.create_all(engine)
        Session.configure(bind=engine)
        session = Session()

        last_records = {
            record.country: record
            for record in session.query(Covid19Update)
            .filter(Covid19Update.country.in_(self.country))
            .all()
        }

        for summary in summaries:
            country = summary['CountryCode']
            last_record = last_records.get(country)
            if (
                not last_record
                or summary['TotalConfirmed'] != last_record.confirmed
                or summary['TotalDeaths'] != last_record.deaths
                or summary['TotalRecovered'] != last_record.recovered
            ):
                self._process_update(summary=summary, session=session)

        session.commit()


# vim:sw=4:ts=4:et:
