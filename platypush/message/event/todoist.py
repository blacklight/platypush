from platypush.message.event import Event


class TodoistEvent(Event):
    pass


class NewItemEvent(TodoistEvent):
    """
    Event triggered when a new item is created.
    """

    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, item=item, **kwargs)


class RemovedItemEvent(TodoistEvent):
    """
    Event triggered when a new item is removed.
    """

    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, item=item, **kwargs)


class ModifiedItemEvent(TodoistEvent):
    """
    Event triggered when an item is changed.
    """

    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, item=item, **kwargs)


class CheckedItemEvent(ModifiedItemEvent):
    """
    Event triggered when an item is checked.
    """

    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, item=item, **kwargs)


class ItemContentChangeEvent(ModifiedItemEvent):
    """
    Event triggered when the content of an item changes.
    """

    def __init__(self, item, *args, **kwargs):
        super().__init__(*args, item=item, **kwargs)


class TodoistSyncRequiredEvent(TodoistEvent):
    """
    Event triggered when an event occurs that doesn't fall into the categories above.
    """


# vim:sw=4:ts=4:et:
