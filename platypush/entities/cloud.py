from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from platypush.common.db import is_defined

from .devices import Device


if not is_defined('cloud_instance'):

    class CloudInstance(Device):
        """
        Entity that maps a cloud node - like a Linode or AWS instance.
        """

        __tablename__ = 'cloud_instance'

        id = Column(
            Integer, ForeignKey(Device.id, ondelete='CASCADE'), primary_key=True
        )

        status = Column(String)
        instance_type = Column(String)
        ipv4_addresses = Column(JSON)
        ipv6_address = Column(String)
        group = Column(String)
        tags = Column(JSON)
        image = Column(String)
        region = Column(String)
        hypervisor = Column(String)
        uuid = Column(String)
        specs = Column(JSON)
        alerts = Column(JSON)
        backups = Column(JSON)

        __table_args__ = {'extend_existing': True}
        __mapper_args__ = {
            'polymorphic_identity': __tablename__,
        }
