import json

from platypush.message.event import Event


class NFCEvent(Event):
    """
    Generic class for NFC events
    """

    def __init__(self, reader=None, tag_id=None, *args, **kwargs):
        super().__init__(reader=reader, tag_id=tag_id, *args, **kwargs)


class NFCDeviceConnectedEvent(NFCEvent):
    """
    Event triggered when an NFC reader/writer devices is connected
    """

    def __init__(self, reader=None, *args, **kwargs):
        """
        :param reader: Name or address of the reader that fired the event
        :type reader: str
        """
        super().__init__(reader=reader, *args, **kwargs)


class NFCDeviceDisconnectedEvent(NFCEvent):
    """
    Event triggered when an NFC reader/writer devices is disconnected
    """

    def __init__(self, reader=None, *args, **kwargs):
        """
        :param reader: Name or address of the reader that fired the event
        :type reader: str
        """
        super().__init__(reader=reader, *args, **kwargs)


class NFCTagDetectedEvent(NFCEvent):
    """
    Event triggered when an NFC tag is connected
    """

    def __init__(self, reader=None, tag_id=None, records=None, *args, **kwargs):
        """
        :param reader: Name or address of the reader that fired the event
        :type reader: str

        :param tag_id: ID of the NFC tag
        :type tag_id: str

        :param records: Optional, list of records read from the tag. If the tag contains JSON-serializable data then it
            will be cast by the backend into the appropriate object
        :type records: str, bytes or JSON-serializable object
        """
        if not records:
            records = []

        super().__init__(reader=reader, tag_id=tag_id, records=records, *args, **kwargs)


class NFCTagRemovedEvent(NFCEvent):
    """
    Event triggered when a NFC card is removed/disconnected
    """

    def __init__(self, reader=None, tag_id=None, *args, **kwargs):
        """
        :param reader: Name or address of the reader that fired the event
        :type reader: str

        :param tag_id: ID of the NFC tag
        :type tag_id: str
        """
        super().__init__(reader=reader, tag_id=tag_id, *args, **kwargs)


# vim:sw=4:ts=4:et:
