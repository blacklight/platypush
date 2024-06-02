import os
from typing import Optional, Sequence

from platypush.context import get_plugin
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin
from platypush.plugins.tts.picovoice import TtsPicovoicePlugin

from ._assistant import Assistant
from ._state import AssistantState


# pylint: disable=too-many-ancestors
class AssistantPicovoicePlugin(AssistantPlugin, RunnablePlugin):
    r"""
    A voice assistant that runs on your device, based on the `Picovoice
    <https://picovoice.ai/>`_ engine.

    Picovoice is a suite of on-device voice technologies that include:

        * **Porcupine**: wake-word engine, if you want the device to listen for
          a specific wake word in order to start the assistant.

        * **Cheetah**: speech-to-text engine, if you want your voice
          interactions to be transcribed into free text - either
          programmatically or when triggered by the wake word. Or:

        * **Rhino**: intent recognition engine, if you want to extract *intents*
          out of your voice commands - for instance, the phrase "set the living
          room temperature to 20 degrees" could be mapped to the intent with the
          following parameters: ``intent``: ``set_temperature``, ``room``:
          ``living_room``, ``temperature``: ``20``.

        * **Leopard**: speech-to-text engine aimed at offline transcription of
          audio files rather than real-time transcription.

        * **Orca**: text-to-speech engine, if you want to create your custom
          logic to respond to user's voice commands and render the responses as
          audio.

    This plugin is a wrapper around the Picovoice engine that allows you to
    run your custom voice-based conversational flows on your device.

    Getting a Picovoice account and access key
    -------------------------------------------

    You can get your personal access key by signing up at the `Picovoice
    console <https://console.picovoice.ai/>`_. You may be asked to submit a
    reason for using the service (feel free to mention a personal Platypush
    integration), and you will receive your personal access key.

    If prompted to select the products you want to use, make sure to select
    the ones from the Picovoice suite that you want to use with this plugin.


    Hotword detection
    -----------------

    The hotword detection engine is based on `Porcupine
    <https://picovoice.ai/platform/porcupine/>`_.

    If enabled through the ``hotword_enabled`` parameter (default: True), the
    assistant will listen for a specific wake word before starting the
    speech-to-text or intent recognition engines. You can specify custom models
    for your hotword (e.g. on the same device you may use "Alexa" to trigger the
    speech-to-text engine in English, "Computer" to trigger the speech-to-text
    engine in Italian, and "Ok Google" to trigger the intent recognition engine.

    You can also create your custom hotword models using the `Porcupine console
    <https://console.picovoice.ai/ppn>`_.

    If ``hotword_enabled`` is set to True, you must also specify the
    ``keywords`` parameter with the list of keywords that you want to listen
    for, and optionally the ``keyword_paths`` parameter with the paths to the
    any custom hotword models that you want to use. If ``hotword_enabled`` is
    set to False, then the assistant won't start listening for speech after the
    plugin is started, and you will need to programmatically start the
    conversation by calling the :meth:`.start_conversation` action, or trigger
    it from the UI.

    When a wake-word is detected, the assistant will emit a
    :class:`platypush.message.event.assistant.HotwordDetectedEvent` event that
    you can use to build your custom logic. For example:

      .. code-block:: python

        import time

        from platypush import when, run
        from platypush.message.event.assistant import HotwordDetectedEvent

        # Turn on a light for 5 seconds when the hotword "Alexa" is detected
        @when(HotwordDetectedEvent, hotword='Alexa')
        def on_hotword_detected(event: HotwordDetectedEvent, **context):
            run("light.hue.on", lights=["Living Room"])
            time.sleep(5)
            run("light.hue.off", lights=["Living Room"])

    By default, the assistant will start listening for speech after the hotword
    if either ``stt_enabled`` or ``intent_model_path`` are set. If you don't
    want the assistant to start listening for speech after the hotword is
    detected (for example because you want to build your custom response flows,
    or trigger the speech detection using different models depending on the
    hotword that is used, or because you just want to detect hotwords but not
    speech), then you can also set the ``start_conversation_on_hotword``
    parameter to ``False``. If that is the case, then you can programmatically
    start the conversation by calling the :meth:`.start_conversation` method in
    your event hooks:

      .. code-block:: python

        from platypush import when, run
        from platypush.message.event.assistant import HotwordDetectedEvent

        # Start a conversation using the Italian language model when the
        # "Buongiorno" hotword is detected
        @when(HotwordDetectedEvent, hotword='Buongiorno')
        def on_it_hotword_detected(event: HotwordDetectedEvent, **context):
            event.assistant.start_conversation(model_file='path/to/it.pv')

    Speech-to-text
    --------------

    The speech-to-text engine is based on `Cheetah
    <https://picovoice.ai/docs/cheetah/>`_.

    If enabled through the ``stt_enabled`` parameter (default: True), the
    assistant will transcribe the voice commands into text when a conversation
    is started either programmatically through :meth:`.start_conversation` or
    when the hotword is detected.

    It will emit a
    :class:`platypush.message.event.assistant.SpeechRecognizedEvent` when some
    speech is detected, and you can hook to that event to build your custom
    logic:

      .. code-block:: python

        from platypush import when, run
        from platypush.message.event.assistant import SpeechRecognizedEvent

        # Turn on a light when the phrase "turn on the lights" is detected.
        # Note that we can leverage regex-based pattern matching to be more
        # flexible when matching the phrases. For example, the following hook
        # will be matched when the user says "turn on the lights", "turn on
        # lights", "lights on", "lights on please", "turn on light" etc.
        @when(SpeechRecognizedEvent, phrase='turn on (the)? lights?')
        def on_turn_on_lights(event: SpeechRecognizedEvent, **context):
            run("light.hue.on")

    You can also leverage context extraction through the ``${}`` syntax on the
    hook to extract specific tokens from the event that can be passed to your
    event hook. For example:

      .. code-block:: python

        from platypush import when, run
        from platypush.message.event.assistant import SpeechRecognizedEvent

        @when(SpeechRecognizedEvent, phrase='play ${title} by ${artist}')
        def on_play_track_command(
            event: SpeechRecognizedEvent, title: str, artist: str, **context
        ):
            results = run(
                "music.mopidy.search",
                filter={"title": title, "artist": artist}
            )

            if not results:
                event.assistant.render_response(f"Couldn't find {title} by {artist}")
                return

            run("music.mopidy.play", resource=results[0]["uri"])

    Speech-to-intent
    ----------------

    The intent recognition engine is based on `Rhino
    <https://picovoice.ai/docs/rhino/>`_.

    *Intents* are snippets of unstructured transcribed speech that can be
    matched to structured actions.

    Unlike with hotword and speech-to-text detection, you need to provide a
    custom model for intent detection. You can create your custom model using
    the `Rhino console <https://console.picovoice.ai/rhn>`_.

    When an intent is detected, the assistant will emit a
    :class:`platypush.message.event.assistant.IntentRecognizedEvent` that can
    be listened.

    For example, you can train a model to control groups of smart lights by
    defining the following slots on the Rhino console:

        - ``device_state``: The new state of the device (e.g. with ``on`` or
          ``off`` as supported values)

        - ``room``: The name of the room associated to the group of lights to
          be controlled (e.g. ``living room``, ``kitchen``, ``bedroom``)

    You can then define a ``lights_ctrl`` intent with the following expressions:

        - "turn ``$device_state:state`` the lights"
        - "turn ``$device_state:state`` the ``$room:room`` lights"
        - "turn the lights ``$device_state:state``"
        - "turn the ``$room:room`` lights ``$device_state:state``"
        - "turn ``$room:room`` lights ``$device_state:state``"

    This intent will match any of the following phrases:

        - "*turn on the lights*"
        - "*turn off the lights*"
        - "*turn the lights on*"
        - "*turn the lights off*"
        - "*turn on the living room lights*"
        - "*turn off the living room lights*"
        - "*turn the living room lights on*"
        - "*turn the living room lights off*"

    And it will extract any slots that are matched in the phrases in the
    :class:`platypush.message.event.assistant.IntentRecognizedEvent` event.

    Train the model, download the context file, and pass the path on the
    ``intent_model_path`` parameter.

    You can then register a hook to listen to a specific intent:

      .. code-block:: python

        from platypush import when, run
        from platypush.message.event.assistant import IntentRecognizedEvent

        @when(IntentRecognizedEvent, intent='lights_ctrl', slots={'state': 'on'})
        def on_turn_on_lights(event: IntentRecognizedEvent, **context):
            room = event.slots.get('room')
            if room:
                run("light.hue.on", groups=[room])
            else:
                run("light.hue.on")

    Note that if both ``stt_enabled`` and ``intent_model_path`` are set, then
    both the speech-to-text and intent recognition engines will run in parallel
    when a conversation is started.

    The intent engine is usually faster, as it has a smaller set of intents to
    match and doesn't have to run a full speech-to-text transcription. This means that,
    if an utterance matches both a speech-to-text phrase and an intent, the
    :class:`platypush.message.event.assistant.IntentRecognizedEvent` event is emitted
    (and not :class:`platypush.message.event.assistant.SpeechRecognizedEvent`).

    This may not be always the case though. So it may be a good practice to
    also provide a fallback
    :class:`platypush.message.event.assistant.SpeechRecognizedEvent` hook to
    catch the text if the speech is not recognized as an intent:

      .. code-block:: python

        from platypush import when, run
        from platypush.message.event.assistant import SpeechRecognizedEvent

        @when(SpeechRecognizedEvent, phrase='turn ${state} (the)? ${room} lights?')
        def on_turn_on_lights(event: SpeechRecognizedEvent, phrase, room, **context):
            if room:
                run("light.hue.on", groups=[room])
            else:
                run("light.hue.on")

    Text-to-speech
    --------------

    The text-to-speech engine is based on `Orca
    <https://picovoice.ai/docs/orca/>`_.

    It is not directly implemented by this plugin, but the implementation is
    provided in the :class:`platypush.plugins.tts.picovoice.TtsPicovoicePlugin`
    plugin.

    You can however leverage the :meth:`.render_response` action to render some
    text as speech in response to a user command, and that in turn will leverage
    the PicoVoice TTS plugin to render the response.

    For example, the following snippet provides a hook that:

        - Listens for
          :class:`platypush.message.event.assistant.SpeechRecognizedEvent`.

        - Matches the phrase against a list of predefined commands that
          shouldn't require a response.

        - Has a fallback logic that leverages the
          :class:`platypush.plugins.openai.OpenaiPlugin` to generate a response
          for the given text and renders it as speech.

        - Has a logic for follow-on turns if the response from ChatGPT is a question.

      .. code-block:: python

        import re
        from collections import defaultdict
        from datetime import datetime as dt, timedelta
        from dateutil.parser import isoparse
        from logging import getLogger

        from platypush import hook, run
        from platypush.message.event.assistant import (
            SpeechRecognizedEvent,
            ResponseEndEvent,
        )

        logger = getLogger(__name__)

        def play_music(*_, **__):
            run("music.mopidy.play")

        def stop_music(*_, **__):
            run("music.mopidy.stop")

        def ai_assist(event: SpeechRecognizedEvent, **__):
            response = run("openai.get_response", prompt=event.phrase)
            if not response:
                return

            run("assistant.picovoice.render_response", text=response)

        # List of commands to match, as pairs of regex patterns and the
        # corresponding actions
        hooks = (
            (re.compile(r"play (the)?music", re.IGNORECASE), play_music),
            (re.compile(r"stop (the)?music", re.IGNORECASE), stop_music),
            # Fallback to the AI assistant
            (re.compile(r".*"), ai_assist),
        )

        @when(SpeechRecognizedEvent)
        def on_speech_recognized(event, **kwargs):
            for pattern, command in hooks:
                if pattern.search(event.phrase):
                    logger.info("Running voice command %s", command.__name__)
                    command(event, **kwargs)
                    break

        @when(ResponseEndEvent)
        def on_response_end(event: ResponseEndEvent, **__):
            # Check if the response is a question and start a follow-on turn if so.
            # Note that the ``openai`` plugin by default is configured to keep
            # the past interaction in a context window of ~10 minutes, so you
            # can follow up like in a real conversation.
            if event.assistant and event.response_text and event.response_text.endswith("?"):
                event.assistant.start_conversation()

    """

    def __init__(
        self,
        access_key: str,
        hotword_enabled: bool = True,
        stt_enabled: bool = True,
        keywords: Optional[Sequence[str]] = None,
        keyword_paths: Optional[Sequence[str]] = None,
        keyword_model_path: Optional[str] = None,
        speech_model_path: Optional[str] = None,
        intent_model_path: Optional[str] = None,
        endpoint_duration: Optional[float] = 0.5,
        enable_automatic_punctuation: bool = False,
        start_conversation_on_hotword: bool = True,
        audio_queue_size: int = 100,
        conversation_timeout: Optional[float] = 7.5,
        muted: bool = False,
        **kwargs,
    ):
        """
        :param access_key: Your Picovoice access key. You can get it by signing
            up at the `Picovoice console <https://console.picovoice.ai/>`.
        :param hotword_enabled: Enable the wake-word engine (default: True).
            **Note**: The wake-word engine requires you to add Porcupine to the
            products available in your Picovoice account.
        :param stt_enabled: Enable the speech-to-text engine (default: True).
            **Note**: The speech-to-text engine requires you to add Cheetah to
            the products available in your Picovoice account.
        :param keywords: List of keywords to listen for (e.g. ``alexa``, ``ok
            google``...). This is required if the wake-word engine is enabled.
            See the `Porcupine keywords repository
            <https://github.com/Picovoice/porcupine/tree/master/resources/keyword_files>`_).
            for a list of the stock keywords available. If you have a custom
            model, you can pass its path to the ``keyword_paths`` parameter and
            its filename (without the path and the platform extension) here.
        :param keyword_paths: List of paths to the keyword files to listen for.
            Custom keyword files can be created using the `Porcupine console
            <https://console.picovoice.ai/ppn>`_ and downloaded from the
            console itself.
        :param keyword_model_path: If you are using a keyword file in a
            non-English language, you can provide the path to the model file
            for its language. Model files are available for all the supported
            languages through the `Porcupine lib repository
            <https://github.com/Picovoice/porcupine/tree/master/lib/common>`_.
        :param speech_model_path: Path to the speech model file. If you are
            using a language other than English, you can provide the path to the
            model file for that language. Model files are available for all the
            supported languages through the `Cheetah repository
            <https://github.com/Picovoice/cheetah/tree/master/lib/common>`_.
            You can also use the `Speech console
            <https://console.picovoice.ai/cat>`_
            to train your custom models. You can use a base model and fine-tune
            it by boosting the detection of your own words and phrases and edit
            the phonetic representation of the words you want to detect.
        :param intent_model_path: Path to the Rhino context model. This is
            required if you want to use the intent recognition engine through
            Rhino. The context model is a file that contains a list of intents
            that can be recognized by the engine. An intent is an action or a
            class of actions that the assistant can recognize, and it can
            contain an optional number of slots to model context variables -
            e.g. temperature, lights group, location, device state etc.
            You can create your own context model using the `Rhino console
            <https://console.picovoice.ai/rhn>`_. For example, you can define a
            context file to control smart home devices by defining the
            following slots:

                - ``device_type``: The device to control (e.g. lights, music)
                - ``device_state``: The target state of the device (e.g. on,
                  off)
                - ``location``: The location of the device (e.g. living
                  room, kitchen, bedroom)
                - ``media_type``: The type of media to play (e.g. music, video)
                - ``media_state``: The state of the media (e.g. play, pause,
                  stop)

            You can then define the following intents:

                - ``device_ctrl``: Control a device state. Supported phrases:
                    - "turn ``$device_state:state`` the ``$location:location``
                      ``$device_type:device``"
                    - "turn ``$device_state:state`` the ``$device_type:device``"

                - ``media_ctrl``: Control media state. Supported phrases:
                    - "``$media_state:state`` the ``$media_type:media``"
                    - "``$media_state:state`` the ``$media_type:media`` in the
                      ``$location:location``"

            Then a phrase like "turn on the lights in the living room" would
            trigger a
            :class:`platypush.message.event.assistant.IntentRecognizedEvent` with:

                .. code-block:: json

                  {
                    "intent": "device_ctrl",
                    "slots": {
                      "type": "lights",
                      "state": "on",
                      "location": "living room"
                    }
                  }

            **Note**: The intent recognition engine requires you to add Rhino
            to the products available in your Picovoice account.
        :param endpoint_duration: If set, the assistant will stop listening when
            no speech is detected for the specified duration (in seconds) after
            the end of an utterance.
        :param enable_automatic_punctuation: Enable automatic punctuation
            insertion.
        :param start_conversation_on_hotword: If set to True (default), a speech
            detection session will be started when the hotword is detected. If
            set to False, you may want to start the conversation programmatically
            by calling the :meth:`.start_conversation` method instead, or run any
            custom logic hotword detection logic. This can be particularly useful
            when you want to run the assistant in a push-to-talk mode, or when you
            want different hotwords to trigger conversations with different models
            or languages.
        :param audio_queue_size: Maximum number of audio frames to hold in the
            processing queue. You may want to increase this value if you are
            running this integration on a slow device and/or the logs report
            audio frame drops too often. Keep in mind that increasing this value
            will increase the memory usage of the integration. Also, a higher
            value may result in higher accuracy at the cost of higher latency.
        :param conversation_timeout: Maximum time to wait for some speech to be
            detected after the hotword is detected. If no speech is detected
            within this time, the conversation will time out and the plugin will
            go back into hotword detection mode, if the mode is enabled. Default:
            7.5 seconds.
        :param muted: Set to True to start the assistant in a muted state. You will
            need to call the :meth:`.unmute` method to start the assistant listening
            for commands, or programmatically call the :meth:`.start_conversation`
            to start a conversation.
        """
        super().__init__(**kwargs)
        self._assistant = None
        self._assistant_args = {
            'stop_event': self._should_stop,
            'access_key': access_key,
            'hotword_enabled': hotword_enabled,
            'stt_enabled': stt_enabled,
            'keywords': keywords,
            'keyword_paths': (
                os.path.expanduser(keyword_path)
                for keyword_path in (keyword_paths or [])
            ),
            'keyword_model_path': (
                os.path.expanduser(keyword_model_path) if keyword_model_path else None
            ),
            'speech_model_path': (
                os.path.expanduser(speech_model_path) if speech_model_path else None
            ),
            'intent_model_path': (
                os.path.expanduser(intent_model_path) if intent_model_path else None
            ),
            'endpoint_duration': endpoint_duration,
            'enable_automatic_punctuation': enable_automatic_punctuation,
            'start_conversation_on_hotword': (
                start_conversation_on_hotword
                if (intent_model_path or stt_enabled)
                else False
            ),
            'audio_queue_size': audio_queue_size,
            'conversation_timeout': conversation_timeout,
            'muted': muted,
            'on_conversation_start': self._on_conversation_start,
            'on_conversation_end': self._on_conversation_end,
            'on_conversation_timeout': self._on_conversation_timeout,
            'on_speech_recognized': self._on_speech_recognized,
            'on_intent_matched': self._on_intent_matched,
            'on_hotword_detected': self._on_hotword_detected,
        }

    @property
    def tts(self) -> TtsPicovoicePlugin:
        p = get_plugin('tts.picovoice')
        assert p, 'Picovoice TTS plugin not configured/found'
        return p

    def _get_tts_plugin(self) -> TtsPicovoicePlugin:
        return self.tts

    def _on_response_render_start(self, text: Optional[str], *_, **__):
        if self._assistant:
            self._assistant.set_responding(True)
        return super()._on_response_render_start(text)

    def _on_response_render_end(self, *_, **__):
        if self._assistant:
            self._assistant.set_responding(False)

        return super()._on_response_render_end()

    @action
    def start_conversation(self, *_, model_file: Optional[str] = None, **__):
        """
        Programmatically start a conversation with the assistant.

        :param model_file: Override the model file to be used to detect speech
            in this conversation. If not set, the configured
            ``speech_model_path`` will be used.
        """
        if not self._assistant:
            self.logger.warning('Assistant not initialized')
            return

        if not model_file:
            model_file = self._assistant_args['speech_model_path']
        if model_file:
            model_file = os.path.expanduser(model_file)

        self._assistant.override_speech_model(model_file)
        self._assistant.state = AssistantState.DETECTING_SPEECH

    def _stop_conversation(self, *_, **__):
        super()._stop_conversation()
        if not self._assistant:
            self.logger.warning('Assistant not initialized')
            return

        self._assistant.override_speech_model(None)

        if self._assistant.hotword_enabled:
            self._assistant.state = AssistantState.DETECTING_HOTWORD
        else:
            self._assistant.state = AssistantState.IDLE

    @action
    def say(self, text: str, *args, **kwargs):
        """
        Proxy to
        :class:`platypush.plugins.tts.picovoice.TtsPicovoicePlugin.say` to
        render some text as speech through the Picovoice TTS engine.

        Extra arguments to
        :class:`platypush.plugins.tts.picovoice.TtsPicovoicePlugin.say` can be
        passed over ``args`` and ``kwargs``.

        :param text: Text to be rendered as speech.
        """
        return self.tts.say(text, *args, **kwargs)

    @action
    def transcribe(self, audio_file: str, *_, model_file: Optional[str] = None, **__):
        """
        Transcribe an audio file to text using the `Leopard
        <https://picovoice.ai/docs/leopard/>`_ engine.

        :param text: Text to be transcribed.
        :param model_file: Override the model file to be used to detect speech
            in this conversation. If not set, the configured
            ``speech_model_path`` will be used.
        :return: dict

          .. code-block:: json

            {
              "transcription": "This is a test",
              "words": [
                {
                  "word": "this",
                  "start": 0.06400000303983688,
                  "end": 0.19200000166893005,
                  "confidence": 0.9626294374465942
                },
                {
                  "word": "is",
                  "start": 0.2879999876022339,
                  "end": 0.35199999809265137,
                  "confidence": 0.9781675934791565
                },
                {
                  "word": "a",
                  "start": 0.41600000858306885,
                  "end": 0.41600000858306885,
                  "confidence": 0.9764975309371948
                },
                {
                  "word": "test",
                  "start": 0.5120000243186951,
                  "end": 0.8320000171661377,
                  "confidence": 0.9511580467224121
                }
              ]
            }

        """
        import pvleopard

        audio_file = os.path.expanduser(audio_file)
        if not model_file:
            model_file = self._assistant_args['speech_model_path']
        if model_file:
            model_file = os.path.expanduser(model_file)

        leopard = pvleopard.create(
            access_key=self._assistant_args['access_key'], model_path=model_file
        )

        transcript, words = leopard.process_file(audio_file)

        try:
            return {
                'transcription': transcript,
                'words': [
                    {
                        'word': word.word,
                        'start': word.start_sec,
                        'end': word.end_sec,
                        'confidence': word.confidence,
                    }
                    for word in words
                ],
            }
        finally:
            leopard.delete()

    @action
    def mute(self, *_, **__):
        """
        Mute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=True``.
        """
        return self.set_mic_mute(muted=True)

    @action
    def unmute(self, *_, **__):
        """
        Unmute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=False``.
        """
        return self.set_mic_mute(muted=False)

    @action
    def set_mic_mute(self, muted: bool):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """
        if self._assistant:
            self._assistant.set_mic_mute(muted)

        super()._on_mute_changed(muted)

    @action
    def toggle_mute(self, *_, **__):
        """
        Toggle the mic mute state.
        """
        return self.set_mic_mute(not self._is_muted)

    @action
    def send_text_query(self, *_, query: str, **__):
        """
        Send a text query to the assistant.

        This is equivalent to saying something to the assistant.

        :param query: Query to be sent.
        """
        self._on_speech_recognized(query)

    def main(self):
        while not self.should_stop():
            self.logger.info('Starting Picovoice assistant')
            with Assistant(**self._assistant_args) as self._assistant:
                try:
                    for event in self._assistant:
                        if event is not None:
                            self.logger.debug('Dequeued assistant event: %s', event)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error('Picovoice assistant error: %s', e, exc_info=True)
                    self.wait_stop(5)

    def stop(self):
        try:
            self.stop_conversation()
        except RuntimeError:
            pass

        super().stop()


# vim:sw=4:ts=4:et:
