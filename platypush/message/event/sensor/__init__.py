from platypush.message.event import Event


class SensorDataChangeEvent(Event):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        self.data = data


class SensorDataAboveThresholdEvent(Event):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        self.data = data


class SensorDataBelowThresholdEvent(Event):
    def __init__(self, data, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        self.data = data


# vim:sw=4:ts=4:et:


