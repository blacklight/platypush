import os
from typing import Optional, Union

import numpy as np
import wave

from platypush.message.response.stt import SpeechDetectedResponse
from platypush.plugins import action
from platypush.plugins.stt import SttPlugin


class SttDeepspeechPlugin(SttPlugin):
    """
    This plugin performs speech-to-text and speech detection using the
    `Mozilla DeepSpeech <https://github.com/mozilla/DeepSpeech>`_ engine.

    Requires:

        * **deepspeech** (``pip install 'deepspeech>=0.6.0'``)
        * **numpy** (``pip install numpy``)
        * **sounddevice** (``pip install sounddevice``)

    """

    def __init__(self,
                 model_file: str,
                 lm_file: str,
                 trie_file: str,
                 lm_alpha: float = 0.75,
                 lm_beta: float = 1.85,
                 beam_width: int = 500,
                 *args, **kwargs):
        """
        In order to run the speech-to-text engine you'll need to download the right model files for the
        Deepspeech engine that you have installed:

        .. code-block:: shell

            # Create the working folder for the models
            export MODELS_DIR=~/models
            mkdir -p $MODELS_DIR
            cd $MODELS_DIR

            # Download and extract the model files for your version of Deepspeech. This may take a while.
            export DEEPSPEECH_VERSION=0.6.1
            wget https://github.com/mozilla/DeepSpeech/releases/download/v$DEEPSPEECH_VERSION/deepspeech-$DEEPSPEECH_VERSION-models.tar.gz
            tar -xvzf deepspeech-$DEEPSPEECH_VERSION-models.tar.gz
            x deepspeech-0.6.1-models/
            x deepspeech-0.6.1-models/lm.binary
            x deepspeech-0.6.1-models/output_graph.pbmm
            x deepspeech-0.6.1-models/output_graph.pb
            x deepspeech-0.6.1-models/trie
            x deepspeech-0.6.1-models/output_graph.tflite

        :param model_file: Path to the model file (usually named ``output_graph.pb`` or ``output_graph.pbmm``).
            Note that ``.pbmm`` usually perform better and are smaller.

        :param lm_file: Path to the language model binary file (usually named ``lm.binary``).
        :param trie_file: The path to the trie file build from the same vocabulary as the language model binary
            (usually named ``trie``).
        :param lm_alpha: The alpha hyperparameter of the CTC decoder - Language Model weight.
            See <https://github.com/mozilla/DeepSpeech/releases/tag/v0.6.0>.
        :param lm_beta: The beta hyperparameter of the CTC decoder - Word Insertion weight.
            See <https://github.com/mozilla/DeepSpeech/releases/tag/v0.6.0>.
        :param beam_width:  Decoder beam width (see beam scoring in KenLM language model).
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

        import deepspeech
        super().__init__(*args, **kwargs)
        self.model_file = os.path.abspath(os.path.expanduser(model_file))
        self.lm_file = os.path.abspath(os.path.expanduser(lm_file))
        self.trie_file = os.path.abspath(os.path.expanduser(trie_file))
        self.lm_alpha = lm_alpha
        self.lm_beta = lm_beta
        self.beam_width = beam_width
        self._model: Optional[deepspeech.Model] = None
        self._context = None

    def _get_model(self):
        import deepspeech
        if not self._model:
            self._model = deepspeech.Model(self.model_file, self.beam_width)
            self._model.enableDecoderWithLM(self.lm_file, self.trie_file, self.lm_alpha, self.lm_beta)

        return self._model

    def _get_context(self):
        if not self._model:
            self._model = self._get_model()
        if not self._context:
            self._context = self._model.createStream()

        return self._context

    @staticmethod
    def convert_frames(frames: Union[np.ndarray, bytes]) -> np.ndarray:
        return np.frombuffer(frames, dtype=np.int16)

    def on_detection_started(self):
        self._context = self._get_context()

    def on_detection_ended(self):
        if self._model and self._context:
            self._model.finishStream()
        self._context = None

    def detect_speech(self, frames) -> str:
        model = self._get_model()
        context = self._get_context()
        model.feedAudioContent(context, frames)
        return model.intermediateDecode(context)

    def on_speech_detected(self, speech: str) -> None:
        super().on_speech_detected(speech)
        if not speech:
            return

        model = self._get_model()
        context = self._get_context()
        model.finishStream(context)
        self._context = None

    @action
    def detect(self, audio_file: str) -> SpeechDetectedResponse:
        """
        Perform speech-to-text analysis on an audio file.

        :param audio_file: Path to the audio file.
        """
        audio_file = os.path.abspath(os.path.expanduser(audio_file))
        wav = wave.open(audio_file, 'r')
        buffer = wav.readframes(wav.getnframes())
        data = self.convert_frames(buffer)
        model = self._get_model()
        speech = model.stt(data)
        return SpeechDetectedResponse(speech=speech)


# vim:sw=4:ts=4:et:
