import threading

from platypush.backend import Backend


class AssistantBackend(Backend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._detection_paused = threading.Event()

    def pause_detection(self):
        self._detection_paused.set()

    def resume_detection(self):
        self._detection_paused.clear()

    def is_detecting(self):
        return not self._detection_paused.is_set()


# vim:sw=4:ts=4:et:
