from io import BytesIO
from threading import Event
from typing import Optional, Union

import numpy as np

from platypush.common.assistant import AudioRecorder
from platypush.common.assistant._state import AudioFrame
from platypush.context import get_plugin
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin
from platypush.plugins.assistant._audio import AudioPreprocessor
from platypush.plugins.openai import OpenaiPlugin

from ._markdown import strip_markdown
from ._state import RecordingState


# pylint: disable=too-many-ancestors
class AssistantOpenaiPlugin(AssistantPlugin, RunnablePlugin):
    """
    A voice assistant based on the OpenAI API.

    It requires the :class:`platypush.plugins.openai.OpenaiPlugin` plugin to be
    configured with an OpenAI API key.

    Hotword detection
    -----------------

    This plugin doesn't have hotword detection, as OpenAI doesn't provide
    an API for that. Instead, the assistant can be started and stopped
    programmatically through the :meth:`.start_conversation` action.

    If you want to implement hotword detection, you can use a separate plugin
    such as
    :class:`platypush.plugins.assistant.picovoice.AssistantPicovoicePlugin`.

    The configuration in this case would be like:

        .. code-block:: yaml

            assistant.picovoice:
              access_key: YOUR_PICOVOICE_ACCESS_KEY

              # List of hotwords to listen for
              keywords:
                - alexa
                - computer
                - ok google

              # Disable speech-to-text and intent recognition, only use hotword
              # detection
              stt_enabled: false
              hotword_enabled: true

              conversation_start_sound: /sound/to/play/when/the/conversation/starts.mp3
              # speech_model_path: /mnt/hd/models/picovoice/cheetah/custom-en.pv
              # intent_model_path: /mnt/hd/models/picovoice/rhino/custom-en-x86.rhn

            openai:
              api_key: YOUR_OPENAI_API_KEY

              # Customize your assistant's context and knowledge base to your
              # liking
              context:
                - role: system
                  content: >
                    You are a 16th century noble lady who talks in
                    Shakespearean English to her peers.

            # Enable the assistant plugin
            assistant.openai:

            # Enable the text-to-speech plugin
            tts.openai:
              # Customize the voice model
              voice: nova

    Then you can call :meth:`.start_conversation` when the hotword is detected
    :class:`platypush.message.event.assistant.HotwordDetectedEvent` is
    triggered:

        .. code-block:: python

            from platypush import run, when
            from platypush.message.event.assistant import HotwordDetectedEvent

            @when(HotwordDetectedEvent)
            # You can also customize it by running a different assistant logic
            # depending on the hotword
            # @when(HotwordDetectedEvent, hotword='computer')
            def on_hotword_detected():
                run("assistant.openai.start_conversation")

    This configuration will:

        1. Start the hotword detection when the application starts.
        2. Start the OpenAI assistant when the hotword is detected.

    AI responses
    ------------

    By default (unless you set ``stop_conversation_on_speech_match`` to ``False``),
    the plugin will:

        1. Process the speech through the OpenAI API (the GPT model to be is
           configurable in the OpenAI plugin ``model`` configuration).

        2. Render the response through the configured ``tts_plugin`` (default:
           ``tts.openai``). If ``tts_plugin`` is not set, then the response will
           be returned as a string.

    Custom speech processing
    ------------------------

    You can create custom hooks on
    :class:`platypush.message.event.assistant.SpeechRecognizedEvent` with
    custom ``phrase`` strings or (regex) patterns. For example:

        .. code-block:: python

            from platypush import run, when
            from platypush.message.event.assistant import SpeechRecognizedEvent

            # Matches any phrase that contains either "play music" or "play the
            # music"
            @when(SpeechRecognizedEvent, phrase='play (the)? music')
            def play_music():
                run('music.mpd.play')

    If at least a custom hook with a non-empty ``phrase`` string is matched,
    then the default response will be disabled. If you still want the assistant
    to say something when the event is handled, you can call
    ``event.assistant.render_response`` on the hook:

        .. code-block:: python

            from datetime import datetime
            from textwrap import dedent
            from time import time

            from platypush import run, when
            from platypush.message.event.assistant import SpeechRecognizedEvent

            @when(SpeechRecognizedEvent, phrase='weather today')
            def weather_forecast(event: SpeechRecognizedEvent):
                limit = time() + 24 * 60 * 60  # 24 hours from now
                forecast = [
                    weather
                    for weather in run("weather.openweathermap.get_forecast")
                    if datetime.fromisoformat(weather["time"]).timestamp() < limit
                ]

                min_temp = round(
                    min(weather["temperature"] for weather in forecast)
                )
                max_temp = round(
                    max(weather["temperature"] for weather in forecast)
                )
                max_wind_gust = round(
                    (max(weather["wind_gust"] for weather in forecast)) * 3.6
                )
                summaries = [weather["summary"] for weather in forecast]
                most_common_summary = max(summaries, key=summaries.count)
                avg_cloud_cover = round(
                    sum(weather["cloud_cover"] for weather in forecast) / len(forecast)
                )

                event.assistant.render_response(
                    dedent(
                        f\"\"\"
                        The forecast for today is: {most_common_summary}, with
                        a minimum of {min_temp} and a maximum of {max_temp}
                        degrees, wind gust of {max_wind_gust} km/h, and an
                        average cloud cover of {avg_cloud_cover}%.
                        \"\"\"
                    )
                )

    Conversation follow-up
    ----------------------

    A conversation will have a follow-up (i.e. the assistant will listen for a
    phrase after rendering a response) if the response is not empty and ends
    with a question mark. If you want to force a follow-up even if the response
    doesn't end with a question mark, you can call :meth:`.start_conversation`
    programmatically from your hooks.
    """

    def __init__(
        self,
        model: str = "whisper-1",
        tts_plugin: Optional[str] = "tts.openai",
        sample_rate: int = 16000,
        frame_size: int = 2000,
        channels: int = 1,
        input_device: Optional[Union[int, str]] = None,
        input_volume: float = 100,
        conversation_start_timeout: float = 5.0,
        conversation_end_timeout: float = 1.0,
        conversation_max_duration: float = 15.0,
        enable_noise_suppression: Optional[bool] = None,
        vad_enabled: bool = True,
        vad_mode: int = 2,
        vad_speech_threshold: float = 0.3,
        energy_vad_threshold: float = 300,
        **kwargs,
    ):
        """
        :param model: OpenAI model to use for audio transcription (default:
            ``whisper-1``).
        :param tts_plugin: Name of the TTS plugin to use for rendering the responses
            (default: ``tts.openai``).
        :param sample_rate: Recording sample rate in Hz (default: 16000).
        :param frame_size: Recording frame size in samples (default: 2000).
            With the default sample rate of 16000, this corresponds to 125 ms
            per frame. Smaller values improve the responsiveness of the speech
            boundary detection at the cost of higher CPU usage.
        :param channels: Number of recording channels (default: 1).
        :param input_device: Audio input device to use for recording. Supported
            formats: PortAudio/sounddevice device index, PortAudio/sounddevice
            device name, or PulseAudio/PipeWire source name (e.g.
            ``alsa_input.usb-...``; requires ``pactl``). Default: system
            default input device.
        :param input_volume: Recording gain, as a percentage. ``100`` means
            unchanged, values below ``100`` attenuate, and values above ``100``
            amplify with clipping. Default: 100.
        :param conversation_start_timeout: How long to wait for the
            conversation to start (i.e. the first non-silent audio frame to be
            detected) before giving up and stopping the recording (default: 5.0
            seconds).
        :param conversation_end_timeout: How many seconds of silence to wait
            after the last non-silent audio frame before stopping the recording
            (default: 1.5 seconds).
        :param conversation_max_duration: Maximum conversation duration in seconds
            (default: 15.0 seconds).
        :param enable_noise_suppression: Whether to enable Speex-based noise
            suppression (requires the ``speexdsp_ns`` package). Reduces
            background noise and improves transcription accuracy, especially
            for distant speech. Default: auto-enabled if the package is
            available.
        :param vad_enabled: Whether to use Voice Activity Detection for
            speech boundary detection (default: True). Uses ``webrtcvad`` if
            available, otherwise falls back to energy-based detection. If
            disabled, every audio frame is treated as speech, so the
            conversation will only end on ``conversation_max_duration`` or
            :meth:`.stop_conversation`.
        :param vad_mode: WebRTC VAD aggressiveness mode, 0–3 (default: 2).
            Higher values are more aggressive at filtering non-speech but
            may miss distant or quiet speech.  Only used when ``webrtcvad``
            is installed.
        :param vad_speech_threshold: Fraction of VAD sub-frames within an
            audio frame that must be classified as speech for the frame to
            be considered as containing speech (default: 0.3).
        :param energy_vad_threshold: RMS energy threshold for the
            energy-based VAD fallback (used when ``webrtcvad`` is not
            installed).  Voices at conversational distance typically
            produce RMS > 300 on int16 scale (~-34 dBFS).  Lower values
            improve sensitivity for distant or quiet speech at the cost
            of more false positives.  Default: 300.
        """
        kwargs["tts_plugin"] = tts_plugin
        super().__init__(**kwargs)

        self._model = model
        self._sample_rate = sample_rate
        self._frame_size = frame_size
        self._channels = channels
        self._input_device = input_device
        self._input_volume = input_volume
        self._conversation_start_timeout = conversation_start_timeout
        self._conversation_end_timeout = conversation_end_timeout
        self._conversation_max_duration = conversation_max_duration
        self._audio_processor = AudioPreprocessor(
            frame_size=frame_size,
            sample_rate=sample_rate,
            enable_noise_suppression=enable_noise_suppression,
            vad_enabled=vad_enabled,
            vad_mode=vad_mode,
            vad_speech_threshold=vad_speech_threshold,
            energy_vad_threshold=energy_vad_threshold,
        )
        self._start_recording_event = Event()
        self._disable_default_response = False
        self._recording_state = RecordingState(
            sample_rate=sample_rate,
            channels=channels,
        )

        self._recorder: Optional[AudioRecorder] = None

    def _is_conversation_ended(self):
        # End if the recording has been stopped
        if not self._recorder or self._recorder.should_stop():
            return True

        # End if we reached the max conversation duration
        if self._recording_state.duration >= self._conversation_max_duration:
            return True

        # End if the conversation hasn't started yet and we reached the
        # conversation start timeout
        if (
            not self._recording_state.conversation_started
            and self._recording_state.duration >= self._conversation_start_timeout
        ):
            return True

        # End if the conversation has started and the user has been silent for
        # more than the conversation end timeout
        if (
            self._recording_state.conversation_started
            and self._recording_state.silence_duration >= self._conversation_end_timeout
        ):
            return True

        return False

    @property
    def _openai(self) -> OpenaiPlugin:
        openai: Optional[OpenaiPlugin] = get_plugin("openai")
        if not openai:
            raise AssertionError(
                "OpenAI plugin not found. "
                "Please configure the `openai` plugin to use `assistant.openai`"
            )
        return openai

    def _get_prediction(self, audio: BytesIO) -> str:
        return self._openai.transcribe_raw(
            audio.getvalue(), extension='mp3', model=self._model
        )

    def _capture_audio(self, recorder: AudioRecorder):
        while not self.should_stop() and not self._is_conversation_ended():
            audio_data = recorder.read()
            if not audio_data:
                continue

            data = audio_data.data.tobytes()
            # VAD runs on the ORIGINAL audio (before noise suppression) so
            # that weak distant speech is not suppressed before detection
            is_speech = self._audio_processor.has_speech(data)
            processed = self._audio_processor.process(data)
            processed_frame = AudioFrame(
                data=np.frombuffer(processed, dtype=audio_data.data.dtype),
                timestamp=audio_data.timestamp,
            )
            self._recording_state.add_audio(processed_frame, is_speech=is_speech)

    def _audio_loop(self):
        while not self.should_stop():
            self._wait_recording_start()
            self._recording_state.reset()
            self._on_conversation_start()

            try:
                with AudioRecorder(
                    stop_event=self._should_stop,
                    sample_rate=self._sample_rate,
                    frame_size=self._frame_size,
                    channels=self._channels,
                    device=self._input_device,
                    volume=self._input_volume,
                ) as self._recorder:
                    self._capture_audio(self._recorder)
            finally:
                if self._recorder:
                    try:
                        self._recorder.stream.close()
                    except Exception as e:
                        self.logger.warning("Error closing the audio stream: %s", e)

                self._recorder = None

            if self._recording_state.is_silent():
                self._on_conversation_timeout()
            else:
                audio = self._recording_state.export_audio()
                text = self._get_prediction(audio)
                self._on_speech_recognized(text)

    def _wait_recording_start(self):
        self._start_recording_event.wait()
        self._start_recording_event.clear()

    def _start_conversation(self, *_, **__):
        self._disable_default_response = False
        self._recording_state.reset()
        self._start_recording_event.set()

    def _stop_conversation(self, *_, **__):
        self._disable_default_response = True
        super()._stop_conversation()
        self._recording_state.reset()
        if self._recorder:
            self._recorder.stop()

        self._on_conversation_end()

    def _on_conversation_end(self):
        self._openai.clear_context()
        super()._on_conversation_end()

    def _on_conversation_timeout(self):
        self._openai.clear_context()
        super()._on_conversation_timeout()

    def _on_speech_recognized(self, phrase: Optional[str]):
        super()._on_speech_recognized(phrase)

        # Dirty hack: wait a bit before stopping the conversation to make sure
        # that there aren't event hooks triggered in other threads that are
        # supposed to handle.
        if self.stop_conversation_on_speech_match:
            self.wait_stop(0.5)
            if self.should_stop():
                return

            if self._disable_default_response:
                self.logger.debug("Default response disabled, skipping response")
                return

        response = strip_markdown(
            self._openai.get_response(phrase, clear_context=False).output
        )
        if response:
            self.render_response(response)
        else:
            self._on_no_response()

    @action
    def start_conversation(self, *_, **__):
        """
        Start a conversation with the assistant. The conversation will be
        automatically stopped after ``conversation_max_duration`` seconds of
        audio, or after ``conversation_start_timeout`` seconds of silence
        with no audio detected, or after ``conversation_end_timeout`` seconds
        after the last non-silent audio frame has been detected, or when the
        :meth:`.stop_conversation` method is called.
        """
        self._start_conversation()

    @action
    def mute(self, *_, **__):
        """
        .. note:: This plugin has no hotword detection, thus no continuous
            audio detection. Speech processing is done on-demand through the
            :meth:`.start_conversation` and :meth:`.stop_conversation` methods.
            Therefore, the :meth:`.mute` and :meth:`.unmute` methods are not
            implemented.
        """
        self.logger.warning(
            "assistant.openai.mute is not implemented because this plugin "
            "has no hotword detection, and the only way to stop a conversation "
            "is by calling stop_conversation()"
        )

    @action
    def unmute(self, *_, **__):
        """
        .. note:: This plugin has no hotword detection, thus no continuous
            audio detection. Speech processing is done on-demand through the
            :meth:`.start_conversation` and :meth:`.stop_conversation` methods.
            Therefore, the :meth:`.mute` and :meth:`.unmute` methods are not
            implemented.
        """
        self.logger.warning(
            "assistant.openai.unmute is not implemented because this plugin "
            "has no hotword detection, and the only way to start a conversation "
            "is by calling start_conversation()"
        )

    @action
    def send_text_query(self, text: str, *_, **__):
        """
        If the ``tts_plugin`` configuration is set, then the assistant will
        process the given text query through
        :meth:`platypush.plugins.openai.OpenaiPlugin.get_response` and render
        the response through the specified TTS plugin.

        :return: The response received from
            :meth:`platypush.plugins.openai.OpenaiPlugin.get_response`.
        """
        response = strip_markdown(
            self._openai.get_response(text, clear_context=False).output
        )
        self.render_response(response)
        return response

    def main(self):
        while not self.should_stop():
            try:
                self._audio_loop()
            except Exception as e:
                self.logger.error("Audio loop error: %s", e, exc_info=True)
                self.wait_stop(5)
            finally:
                self.stop_conversation()

    def stop(self):
        self._stop_conversation()
        super().stop()
