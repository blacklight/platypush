import queue
import threading
from abc import ABC, abstractmethod
from typing import Optional, Union, List

import sounddevice as sd

from platypush.context import get_bus
from platypush.message.event.stt import SpeechDetectionStartedEvent, SpeechDetectionStoppedEvent, SpeechStartedEvent, \
    SpeechDetectedEvent, HotwordDetectedEvent, ConversationDetectedEvent
from platypush.message.response.stt import SpeechDetectedResponse
from platypush.plugins import Plugin, action


class SttPlugin(ABC, Plugin):
    """
    Abstract class for speech-to-text plugins.

    Triggers:

        * :class:`platypush.message.event.stt.SpeechStartedEvent` when speech starts being detected.
        * :class:`platypush.message.event.stt.SpeechDetectedEvent` when speech is detected.
        * :class:`platypush.message.event.stt.SpeechDetectionStartedEvent` when speech detection starts.
        * :class:`platypush.message.event.stt.SpeechDetectionStoppedEvent` when speech detection stops.
        * :class:`platypush.message.event.stt.HotwordDetectedEvent` when a user-defined hotword is detected.
        * :class:`platypush.message.event.stt.ConversationDetectedEvent` when speech is detected after a hotword.

    """

    _thread_stop_timeout = 10.0
    rate = 16000
    channels = 1

    def __init__(self,
                 input_device: Optional[Union[int, str]] = None,
                 hotword: Optional[str] = None,
                 hotwords: Optional[List[str]] = None,
                 conversation_timeout: Optional[float] = None,
                 block_duration: float = 1.0):
        """
        :param input_device: PortAudio device index or name that will be used for recording speech (default: default
            system audio input device).
        :param hotword: When this word is detected, the plugin will trigger a
            :class:`platypush.message.event.stt.HotwordDetectedEvent` instead of a
            :class:`platypush.message.event.stt.SpeechDetectedEvent` event. You can use these events for hooking other
            assistants.
        :param hotwords: Use a list of hotwords instead of a single one.
        :param conversation_timeout: If ``hotword`` or ``hotwords`` are set and ``conversation_timeout`` is set,
            the next speech detected event will trigger a :class:`platypush.message.event.stt.ConversationDetectedEvent`
            instead of a :class:`platypush.message.event.stt.SpeechDetectedEvent` event. You can hook custom hooks
            here to run any logic depending on the detected speech - it can emulate a kind of
            "OK, Google. Turn on the lights" interaction without using an external assistant.
        :param block_duration: Duration of the acquired audio blocks (default: 1 second).
        """

        super().__init__()
        self.input_device = input_device
        self.conversation_timeout = conversation_timeout
        self.block_duration = block_duration

        self.hotwords = set(hotwords or [])
        if hotword:
            self.hotwords = {hotword}

        self._conversation_event = threading.Event()
        self._input_stream: Optional[sd.InputStream] = None
        self._recording_thread: Optional[threading.Thread] = None
        self._detection_thread: Optional[threading.Thread] = None
        self._audio_queue: Optional[queue.Queue] = None

    def _get_input_device(self, device: Optional[Union[int, str]] = None) -> int:
        """
        Get the index of the input device by index or name.

        :param device: Device index or name. If None is set then the function will return the index of the
            default audio input device.
        :return: Index of the audio input device.
        """
        if not device:
            device = self.input_device
        if not device:
            return sd.query_hostapis()[0].get('default_input_device')

        if isinstance(device, int):
            assert device <= len(sd.query_devices())
            return device

        for i, dev in enumerate(sd.query_devices()):
            if dev['name'] == device:
                return i

        raise AssertionError('Device {} not found'.format(device))

    def on_speech_detected(self, speech: str) -> None:
        """
        Hook called when speech is detected. Triggers the right event depending on the current context.

        :param speech: Detected speech.
        """
        speech = speech.strip()

        if self._conversation_event.is_set():
            event = ConversationDetectedEvent(speech=speech)
        elif speech in self.hotwords:
            event = HotwordDetectedEvent(hotword=speech)
            if self.conversation_timeout:
                self._conversation_event.set()
                threading.Timer(self.conversation_timeout, lambda: self._conversation_event.clear()).start()
        else:
            event = SpeechDetectedEvent(speech=speech)

        get_bus().post(event)

    @staticmethod
    def convert_frames(frames:  bytes) -> bytes:
        """
        Conversion method for raw audio frames. It just returns the input frames as bytes. Override it if required
        by your logic.

        :param frames: Input audio frames, as bytes.
        :return: The audio frames as passed on the input. Override if required.
        """
        return frames

    def on_detection_started(self):
        """
        Method called when the ``detection_thread`` starts. Initialize your context variables and models here if
        required.
        """
        pass

    def on_detection_ended(self):
        """
        Method called when the ``detection_thread`` stops. Clean up your context variables and models here.
        """
        pass

    @abstractmethod
    def detect_audio(self, frames) -> str:
        """
        Method called within the ``detection_thread`` when new audio frames have been captured. Must be implemented
        by the derived classes.

        :param frames: Audio frames, as returned by ``convert_frames``.
        :return: Detected text, as a string.
        """
        raise NotImplementedError

    def detection_thread(self) -> None:
        """
        This thread reads frames from ``_audio_queue``, performs the speech-to-text detection and calls
        """
        current_text = ''
        self.logger.debug('Detection thread started')
        self.on_detection_started()

        while self._audio_queue:
            try:
                frames = self._audio_queue.get()
                frames = self.convert_frames(frames)
            except Exception as e:
                self.logger.warning('Error while feeding audio to the model: {}'.format(str(e)))
                continue

            text = self.detect_audio(frames)
            if text == current_text:
                if current_text:
                    self.on_speech_detected(current_text)

                current_text = ''
            else:
                if not current_text:
                    get_bus().post(SpeechStartedEvent())

                self.logger.info('Intermediate speech results: [{}]'.format(text))
                current_text = text

        self.on_detection_ended()
        self.logger.debug('Detection thread terminated')

    def recording_thread(self, block_duration: float, input_device: Optional[str] = None) -> None:
        """
        Recording thread. It reads raw frames from the audio device and dispatches them to ``detection_thread``.

        :param block_duration: Audio blocks duration.
        :param input_device: Input device
        """
        self.logger.debug('Recording thread started')
        device = self._get_input_device(input_device)
        blocksize = int(self.rate * self.channels * block_duration)
        self._input_stream = sd.InputStream(samplerate=self.rate, device=device,
                                            channels=self.channels, dtype='int16', latency=0,
                                            blocksize=blocksize)
        self._input_stream.start()
        get_bus().post(SpeechDetectionStartedEvent())

        while self._input_stream:
            try:
                frames = self._input_stream.read(self.rate)[0]
            except Exception as e:
                self.logger.warning('Error while reading from the audio input: {}'.format(str(e)))
                continue

            self._audio_queue.put(frames)

        get_bus().post(SpeechDetectionStoppedEvent())
        self.logger.debug('Recording thread terminated')

    @abstractmethod
    @action
    def detect(self, audio_file: str) -> SpeechDetectedResponse:
        """
        Perform speech-to-text analysis on an audio file. Must be implemented by the derived classes.

        :param audio_file: Path to the audio file.
        """
        raise NotImplementedError

    def __enter__(self):
        """
        Context manager enter. Starts detection and returns self.
        """
        self.start_detection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit. Stops detection.
        """
        self.stop_detection()

    @action
    def start_detection(self, input_device: Optional[str] = None, seconds: Optional[float] = None,
                        block_duration: Optional[float] = None) -> None:
        """
        Start the speech detection engine.

        :param input_device: Audio input device name/index override
        :param seconds: If set, then the detection engine will stop after this many seconds, otherwise it'll
            start running until ``stop_detection`` is called or application stop.
        :param block_duration: ``block_duration`` override.
        """
        assert not self._input_stream and not self._recording_thread, 'Speech detection is already running'
        block_duration = block_duration or self.block_duration
        input_device = input_device if input_device is not None else self.input_device
        self._audio_queue = queue.Queue()
        self._recording_thread = threading.Thread(
            target=lambda: self.recording_thread(block_duration=block_duration, input_device=input_device))

        self._recording_thread.start()
        self._detection_thread = threading.Thread(target=lambda: self.detection_thread())
        self._detection_thread.start()

        if seconds:
            threading.Timer(seconds, lambda: self.stop_detection()).start()

    @action
    def stop_detection(self) -> None:
        """
        Stop the speech detection engine.
        """
        assert self._input_stream, 'Speech detection is not running'
        self._input_stream.stop(ignore_errors=True)
        self._input_stream.close(ignore_errors=True)
        self._input_stream = None

        if self._recording_thread:
            self._recording_thread.join(timeout=self._thread_stop_timeout)
            self._recording_thread = None

        self._audio_queue = None
        if self._detection_thread:
            self._detection_thread.join(timeout=self._thread_stop_timeout)
            self._detection_thread = None


# vim:sw=4:ts=4:et:
