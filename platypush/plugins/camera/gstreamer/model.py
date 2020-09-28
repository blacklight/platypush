import logging
import threading

from platypush.plugins.camera import CameraInfo, Camera

# noinspection PyPackageRequirements
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')

# noinspection PyPackageRequirements,PyUnresolvedReferences
from gi.repository import GLib, Gst, GstApp

Gst.init(None)


class Pipeline:
    def __init__(self):
        self.pipeline = Gst.Pipeline()
        self.logger = logging.getLogger('gst-pipeline')
        self.loop = Loop()
        self.sink = None

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)
        self.data_ready = threading.Event()
        self.data = None

    def add(self, element_name: str, *args, **props):
        el = Gst.ElementFactory.make(element_name, *args)
        for k, v in props.items():
            if k == 'caps':
                v = Gst.caps_from_string(v)
            el.set_property(k, v)

        self.pipeline.add(el)
        return el

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
            if i == len(elements)-1:
                break
            el.link(elements[i+1])

    def emit(self, signal, *args, **kwargs):
        return self.pipeline.emit(signal, *args, **kwargs)

    def play(self):
        assert self.sink, 'No sink element specified through add_sink()'
        self.pipeline.set_state(Gst.State.PLAYING)
        self.loop.start()

    def pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.loop.stop()

    def on_buffer(self, sink):
        sample = GstApp.AppSink.pull_sample(sink)
        buffer = sample.get_buffer()
        size, offset, maxsize = buffer.get_sizes()
        self.data = buffer.extract_dup(offset, size)
        self.data_ready.set()
        return False

    def on_eos(self, *_, **__):
        self.logger.info('End of stream event received')
        self.stop()

    # noinspection PyUnusedLocal
    def on_error(self, bus, msg):
        self.logger.warning('GStreamer pipeline error: {}'.format(msg.parse_error()))
        self.stop()

    def get_sink(self):
        return self.sink


class Loop(threading.Thread):
    def __init__(self):
        super().__init__()
        self._loop = GLib.MainLoop()

    def run(self):
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


class GStreamerCamera(Camera):
    info: CameraInfo
    object: Pipeline


# vim:sw=4:ts=4:et:
