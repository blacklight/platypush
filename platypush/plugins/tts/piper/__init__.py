import os
import pathlib
import tempfile
import wave
from collections import defaultdict
from threading import RLock
from typing import Optional, Dict

from platypush.config import Config
from platypush.plugins import action
from platypush.plugins.tts import TtsPlugin


class TtsPiperPlugin(TtsPlugin):
    r"""
    Text-to-speech plugin that uses `Piper <https://github.com/OHF-Voice/piper1-gpl>`_,
    a fast and local neural text-to-speech engine.

    Install with:

    .. code-block:: bash

        $ pip install piper-tts

    You will also need to download at least one voice model. You can do so via
    the :meth:`.download_voice` action.

    Voice models are typically stored in ``~/.local/share/piper_tts``.

    The full list of supported voice models is `here
    <https://rhasspy.github.io/piper-samples/>`_.
    """

    def __init__(
        self,
        *,
        model: Optional[str] = None,
        models_dir: Optional[str] = None,
        speaker_id: Optional[int] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w_scale: Optional[float] = None,
        use_cuda: bool = False,
        end_padding: float = 1,
        **kwargs,
    ):
        """
        :param model: Path to the Piper ``.onnx`` default voice model file, or
            model name (e.g. ``en_US-hfc_female-medium``) relative to
            ``models_dir``.
            If not specified, it must be specified when :meth:`.say` is called,
            or a model should be downloaded via :meth:`.download_voice`.
        :param models_dir: Directory where Piper voice models are stored.
            Default: ``<WORKDIR>/piper_tts``.
        :param speaker_id: Default speaker ID for multi-speaker models
            (default: None).
        :param length_scale: Default speaking speed scale. Higher values make
            speech slower (default: voice default, typically 1.0).
        :param noise_scale: Default audio variation / expressiveness scale
            (default: voice default).
        :param noise_w_scale: Default phoneme width variation scale
            (default: voice default).
        :param use_cuda: Whether to use CUDA for GPU acceleration. Requires
            ``onnxruntime-gpu`` to be installed (default: False).
        :param end_padding: Silence, in seconds, to append before closing the
            playback stream. This avoids clipping the tail of short generated
            speech on some audio backends (default: 1).
        :param kwargs: Extra arguments to be passed to the
            :class:`platypush.plugins.tts.TtsPlugin` constructor.
        """
        from piper import PiperVoice

        super().__init__(**kwargs)
        self._models_dir = (
            os.path.expanduser(models_dir)
            if models_dir
            else os.path.join(Config.get_workdir(), "piper_tts")
        )
        self._model = model
        self._speaker_id = speaker_id
        self._length_scale = length_scale
        self._noise_scale = noise_scale
        self._noise_w_scale = noise_w_scale
        self._use_cuda = use_cuda
        self.player_args.setdefault('end_padding', end_padding)
        self._voices: Dict[str, Optional[PiperVoice]] = defaultdict(lambda: None)
        self._voices_locks = defaultdict(RLock)

    def _get_voice(self, model: Optional[str] = None):
        from piper import PiperVoice

        is_default = not model
        if is_default:
            model = self._model
        if not model:
            raise ValueError('model must be specified')

        model_path = os.path.expanduser(model)
        if not model_path.endswith('.onnx'):
            model_path += '.onnx'
        if not os.path.exists(model_path):
            model_path = os.path.join(self._models_dir, model)
            if not model_path.endswith('.onnx'):
                model_path += '.onnx'

        with self._voices_locks[model_path]:
            voice = self._voices[model_path]
            if voice:
                return voice

        voice = self._voices[model_path] = PiperVoice.load(
            model_path, use_cuda=self._use_cuda
        )
        return voice

    @action
    def say(
        self,
        text: str,
        *_,
        model: Optional[str] = None,
        speaker_id: Optional[int] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w_scale: Optional[float] = None,
        output_file: Optional[str] = None,
        **player_args,
    ):
        """
        Say some text.

        :param text: Text to say.
        :param model: Override the default voice model.
        :param speaker_id: Speaker ID override for multi-speaker models.
        :param length_scale: Speaking speed override.
        :param noise_scale: Audio variation override.
        :param noise_w_scale: Phoneme width variation override.
        :param output_file: If set, save the audio to the specified file
            instead of playing it.
        :param player_args: Extends the additional arguments to be passed to
            :meth:`platypush.plugins.sound.SoundPlugin.play` (like volume,
            duration, channels etc.).
        """
        player_args.pop('language', None)
        voice = self._get_voice(model)
        from piper.config import SynthesisConfig

        syn_kwargs = {}
        sid = speaker_id if speaker_id is not None else self._speaker_id
        if sid is not None:
            syn_kwargs['speaker_id'] = sid

        length = length_scale if length_scale is not None else self._length_scale
        noise = noise_scale if noise_scale is not None else self._noise_scale
        noise_w = noise_w_scale if noise_w_scale is not None else self._noise_w_scale

        if length is not None:
            syn_kwargs['length_scale'] = length
        if noise is not None:
            syn_kwargs['noise_scale'] = noise
        if noise_w is not None:
            syn_kwargs['noise_w_scale'] = noise_w

        syn_config = SynthesisConfig(**syn_kwargs)

        if output_file:
            output_file = os.path.expanduser(output_file)
            with wave.open(output_file, 'wb') as wav_file:
                voice.synthesize_wav(text, wav_file, syn_config=syn_config)
            return

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            tmp_path = f.name

        try:
            with wave.open(tmp_path, 'wb') as wav_file:
                voice.synthesize_wav(text, wav_file, syn_config=syn_config)
            player_args["join"] = True
            self._playback(tmp_path, **player_args)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @action
    def download_voice(self, voice: str, models_dir: Optional[str] = None):
        """
        Download a Piper voice model.

        :param voice: Name of the voice to download (e.g.
            ``en_US-lessac-medium``).
        :param models_dir: Directory to store the downloaded voice model
            (default: the configured ``models_dir``).
        """
        import subprocess
        import sys

        cmd = [sys.executable, '-m', 'piper.download_voices', voice]
        models_dir = os.path.expanduser(models_dir or self._models_dir)
        cmd += ['--data-dir', os.path.expanduser(models_dir)]
        pathlib.Path(models_dir).mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            raise RuntimeError(f'Failed to download voice "{voice}": {result.stderr}')

        self.logger.info('Voice "%s" downloaded successfully', voice)


# vim:sw=4:ts=4:et:
