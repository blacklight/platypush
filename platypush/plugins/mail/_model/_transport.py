from enum import IntEnum


class TransportEncryption(IntEnum):
    """
    Enum for mail transport encryption types.
    """

    NONE = 0
    STARTTLS = 1
    SSL = 2

    @classmethod
    def by_url_scheme(cls, scheme: str) -> 'TransportEncryption':
        """
        Get the transport encryption type from the specified URL scheme.
        """
        if scheme.endswith('+starttls'):
            return cls.STARTTLS
        if scheme.endswith('s'):
            return cls.SSL
        return cls.NONE


# vim:sw=4:ts=4:et:
