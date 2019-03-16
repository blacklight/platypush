from platypush.message.event import Event


class GoogleFitEvent(Event):
    """
    Event triggered upon new Google Fit data points
    """

    def __init__(self, data_source_id, values, *args, **kwargs):
        super().__init__(*args, data_source_id=data_source_id, values=values,
                         **kwargs)


# vim:sw=4:ts=4:et:
