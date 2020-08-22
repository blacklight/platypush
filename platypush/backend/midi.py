import time

from threading import Timer

from platypush.backend import Backend
from platypush.message.event.midi import MidiMessageEvent


class MidiBackend(Backend):
    """
    This backend will listen for events from a MIDI device and post a
    MidiMessageEvent whenever a new MIDI event happens.

    Triggers:

        * :class:`platypush.message.event.midi.MidiMessageEvent` when a new MIDI event is received

    Requires:

        * **rtmidi** (``pip install rtmidi``)
    """

    def __init__(self, device_name=None, port_number=None,
                 midi_throttle_time=None, *args, **kwargs):
        """
        :param device_name: Name of the MIDI device.  *N.B.* either
            `device_name` or `port_number` must be set.
            Use :meth:`platypush.plugins.midi.query_ports` to get the
            available ports indices and names
        :type device_name: str

        :param port_number: MIDI port number
        :type port_number: int

        :param midi_throttle_time: If set, the MIDI events will be throttled -
            max one per selected time frame (in seconds). Set this parameter if
            you want to synchronize MIDI events with plugins that normally
            operate with a lower throughput.
        :type midi_throttle_time: int
        """

        import rtmidi
        super().__init__(*args, **kwargs)

        if (device_name and port_number is not None) or \
                (not device_name and port_number is None):
            raise RuntimeError('Either device_name or port_number (not both) ' +
                               'must be set in the MIDI backend configuration')

        self.midi_throttle_time = midi_throttle_time
        self.midi = rtmidi.MidiIn()
        self.last_trigger_event_time = None
        self.midi_flush_timeout = None
        ports = self.midi.get_ports()

        if not ports:
            raise RuntimeError('No MIDI devices available')

        if device_name:
            if device_name not in ports:
                raise RuntimeError('MIDI device "{}" not found'.format(device_name))

            self.port_number = ports.index(device_name)
            self.device_name = device_name

        if port_number:
            if port_number < 0 or port_number >= len(ports):
                raise RuntimeError('MIDI port {} not found')

            self.port_number = port_number
            self.device_name = ports[port_number]

        self.midi.set_callback(self._on_midi_message())

    def _on_midi_message(self):
        def flush_midi_message(message):
            def _f():
                self.logger.info('Flushing throttled MIDI message {} to the bus'.format(message))
                delay = time.time() - self.last_trigger_event_time
                self.bus.post(MidiMessageEvent(message=message, delay=delay))
            return _f

        # noinspection PyUnusedLocal
        def callback(message, data):
            # rtmidi will provide a tuple in the format
            # (midi_message, time_since_last_event)
            delay = message[1]
            message = message[0]

            if self.midi_throttle_time and self.last_trigger_event_time:
                event_delta = time.time() - self.last_trigger_event_time
                if event_delta < self.midi_throttle_time:
                    self.logger.debug('Skipping throttled message {}'.format(message))
                    if self.midi_flush_timeout:
                        self.midi_flush_timeout.cancel()

                    self.midi_flush_timeout = Timer(
                        self.midi_throttle_time-event_delta,
                        flush_midi_message(message))

                    self.midi_flush_timeout.start()
                    return

            self.last_trigger_event_time = time.time()
            self.bus.post(MidiMessageEvent(message=message, delay=delay))

        return callback

    def run(self):
        super().run()

        self.midi.open_port(self.port_number)
        self.logger.info('Initialized MIDI backend, listening for events on device {}'.
                         format(self.device_name))

        while not self.should_stop():
            try:
                time.sleep(1)
            except Exception as e:
                self.logger.exception(e)

        if self.midi:
            self.midi.close_port(self.port_number)
            self.midi = None


# vim:sw=4:ts=4:et:
