import inspect
import logging
import threading


class EventGenerator(object):
    """
    Abstract class for event generators. It allows to fire events to the bus and
    trigger/register/unregister custom callback handlers associated to event
    types. Both plugins and backends extend this class.
    """

    logger = logging.getLogger('platypush')

    def __init__(self, *args, **kwargs):
        self._event_handlers = {}   # Event type => callback map

    def fire_event(self, event):
        """
        Fires an event (instance of :class:`platypush.message.event.Event` or a
            subclass) to the internal bus and triggers any handler callback
            associated to the event type or any of its super-classes.

        :param event: Event to fire
        :type event: :class:`platypush.message.event.Event` or a subclass
        """

        def hndl_thread():
            hndl(event)

        from platypush.backend import Backend
        from platypush.context import get_bus

        bus = self.bus if isinstance(self, Backend) else get_bus()
        if not bus:
            self.logger.warning('No bus available to post the event: {}'.format(event))
        else:
            bus.post(event)

        handlers = set()

        for cls in inspect.getmro(event.__class__):
            if cls in self._event_handlers:
                handlers.update(self._event_handlers[cls])

        for hndl in handlers:
            threading.Thread(target=hndl_thread).start()


    def register_handler(self, event_type, callback):
        """
        Registers a callback handler for a camera event type.

        :param event_type: Event type to listen to. Must be a subclass of
            :class:`platypush.message.event.Event`
        :type event_type: :class:`platypush.message.event.Event` or a subclass

        :param callback: Callback function. It will take an event of type
            :class:`platypush.message.event.Event` as a parameter
        :type callback: function
        """

        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = set()
        self._event_handlers[event_type].add(callback)


    def unregister_handler(self, event_type, callback):
        """
        Unregisters a callback handler from a camera event type.

        :param event_type: Event type the callback is registered to
        :type event_type: :class:`platypush.message.event.Event` or a subclass

        :param callback: Callback function to unregister
        :type callback: function
        """

        if event_type not in self._event_handlers:
            return
        if callback not in self._event_handlers[event_type]:
            return

        self._event_handlers[event_type].remove(callback)

        if not self._event_handlers[event_type]:
            del self._event_handlers[event_type]


# vim:sw=4:ts=4:et:
