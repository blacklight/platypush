import logging
import threading

from typing import Optional

import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')

# flake8: noqa
from gi.repository import GLib, Gst, GstApp

Gst.init(None)


class Pipeline:
    """
    A GStreamer pipeline.
    """

    def __init__(self):
        self.logger = logging.getLogger('gst-pipeline')
        self.pipeline = Gst.Pipeline()
        self.pipeline.set_state(Gst.State.NULL)
        self.loop = Loop()
        self.source = None
        self.sink = None

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.on_message)
        self.data_ready = threading.Event()
        self.data = None
        self._gst_state = Gst.State.NULL

    def add(self, element_name: str, *args, **props):
        el = Gst.ElementFactory.make(element_name, *args)
        for k, v in props.items():
            if k == 'caps':
                v = Gst.caps_from_string(v)
            el.set_property(k, v)

        self.pipeline.add(el)
        return el

    def add_source(self, element_name: str, *args, **props):
        assert not self.source, 'A source element is already set for this pipeline'
        source = self.add(element_name, *args, **props)
        self.source = source
        return source

    def add_sink(self, element_name: str, *args, **props):
        assert not self.sink, 'A sink element is already set for this pipeline'
        sink = self.add(element_name, *args, **props)
        sink.connect('new-sample', self.on_buffer)
        sink.set_property('emit-signals', True)
        self.sink = sink
        return sink

    @staticmethod
    def link(*elements):
        for i, el in enumerate(elements):
            if i == len(elements) - 1:
                break
            el.link(elements[i + 1])

    def emit(self, signal, *args, **kwargs):
        return self.pipeline.emit(signal, *args, **kwargs)

    def play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        assert self.loop, 'No GLib loop is running'
        self.loop.start()

    def pause(self):
        state = self.get_state()
        if state == Gst.State.PAUSED:
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            self.pipeline.set_state(Gst.State.PAUSED)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        if self.loop:
            self.loop.stop()
        self.loop = None

    def get_volume(self) -> float:
        assert self.source, 'No source initialized'
        return self.source.get_property('volume') or 0

    def set_volume(self, volume: float):
        assert self.source, 'No source initialized'
        self.source.set_property('volume', volume)

    def _msg_handler(self, message) -> bool:
        from gi.repository import Gst  # type: ignore[attr-defined]

        if message.type == Gst.MessageType.EOS:
            self.on_eos()
            return True

        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self.on_error(err, debug)
            return True

        if message.type == Gst.MessageType.STATE_CHANGED:
            old_state, new_state, _ = message.parse_state_changed()[:3]
            self.on_state_changed(old_state, new_state)
            return True

        return False  # The message was not handled

    def on_message(self, _, message, *__):
        self._msg_handler(message)

    def on_buffer(self, sink):
        sample = GstApp.AppSink.pull_sample(sink)
        buffer = sample.get_buffer()
        size, offset, _ = buffer.get_sizes()
        self.data = buffer.extract_dup(offset, size)
        self.data_ready.set()
        return False

    def on_eos(self, *_, **__):
        self.logger.info('End of stream event received')
        self.stop()

    def on_state_changed(self, old_state, new_state):
        from gi.repository import Gst  # type: ignore[attr-defined]

        if (
            old_state == new_state
            or new_state == self._gst_state
            or old_state != self._gst_state
        ):
            return

        self._gst_state = new_state

        if new_state == Gst.State.PLAYING:
            self.on_play()
        elif new_state == Gst.State.PAUSED:
            self.on_pause()

    def on_play(self):
        self.logger.debug('GStreamer playback started')

    def on_pause(self):
        self.logger.debug('GStreamer playback paused')

    def on_error(self, _, msg):
        self.logger.warning('GStreamer pipeline error: %s', msg.parse_error())
        self.stop()

    def get_source(self):
        return self.source

    def get_sink(self):
        return self.sink

    def get_state(self) -> Gst.State:
        if not (self.source and self.source.current_state):
            self.logger.warning('Unable to get pipeline state')
            return Gst.State.NULL

        return self.source.current_state

    def is_playing(self) -> bool:
        return self.get_state() == Gst.State.PLAYING

    def is_paused(self) -> bool:
        return self.get_state() == Gst.State.PAUSED

    def get_position(self) -> Optional[float]:
        if not self.source:
            self.logger.warning('Unable to get pipeline state')
            return Gst.State.NULL

        pos = self.source.query_position(Gst.Format(Gst.Format.TIME))
        if not pos[0]:
            return None

        return pos[1] / 1e9

    def get_duration(self) -> Optional[float]:
        assert self.source, 'No active source found'
        pos = self.source.query_duration(Gst.Format(Gst.Format.TIME))
        if not pos[0]:
            return None

        return pos[1] / 1e9

    def is_muted(self) -> bool:
        if not self.source:
            return False
        return self.source.get_property('mute')

    def set_mute(self, mute: bool):
        assert self.source, 'No source specified'
        self.source.set_property('mute', mute)

    def mute(self):
        self.set_mute(True)

    def unmute(self):
        self.set_mute(False)

    def seek(self, position: float):
        assert self.source, 'No source specified'
        position = max(0, position)
        duration = self.get_duration()
        if duration and position > duration:
            position = duration

        seek_ns = int(position * 1e9)
        self.source.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)


class Loop(threading.Thread):
    """
    Wraps the execution of a GLib main loop into its own thread.
    """

    def __init__(self):
        super().__init__()
        self._loop = GLib.MainLoop()

    def run(self):
        assert self._loop, 'No GLib loop is running'
        self._loop.run()

    def is_running(self) -> bool:
        return self.is_alive() or self._loop is not None

    def stop(self):
        if not self.is_running():
            return
        if self._loop:
            self._loop.quit()
        if threading.get_ident() != self.ident:
            self.join()
        self._loop = None


# vim:sw=4:ts=4:et:
