import hashlib
import os
from logging import getLogger
from typing import Optional
from urllib.request import urlretrieve

import numpy as np

from platypush.config import Config

logger = getLogger(__name__)

SILERO_VAD_URL = 'https://github.com/snakers4/silero-vad/raw/v4.0/files/silero_vad.onnx'
SILERO_VAD_MD5 = '03da8de2fec4108a089b39f1b4abefef'


def get_silero_model_path(model_path: Optional[str] = None) -> str:
    """
    Get the path of the Silero VAD ONNX model. If no path is specified, the
    official v4.0 model is downloaded (and checksum-verified) into the
    platypush workdir on first use.
    """
    if model_path:
        path = os.path.expanduser(model_path)
        if not os.path.isfile(path):
            raise FileNotFoundError(f'Silero VAD model not found: {path}')
        return path

    path = os.path.join(Config.get_workdir(), 'assistant', 'models', 'silero_vad.onnx')
    if not os.path.isfile(path):
        _download_model(path)
    return path


def _download_model(path: str):
    logger.info('Downloading the Silero VAD model to %s', path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + '.part'
    urlretrieve(SILERO_VAD_URL, tmp_path)

    with open(tmp_path, 'rb') as f:
        digest = hashlib.md5(f.read()).hexdigest()

    if digest != SILERO_VAD_MD5:
        os.remove(tmp_path)
        raise RuntimeError(f'Checksum mismatch for the Silero VAD model: {digest}')

    os.replace(tmp_path, path)


class SileroVad:
    """
    Speech probability estimator based on the Silero VAD ONNX model (v4
    signature: inputs ``input``, ``sr``, ``h``, ``c``), run through
    ``onnxruntime``. Carries the recurrent state across calls, so it must be
    fed the audio stream in order.
    """

    def __init__(self, model_path: str, sample_rate: int):
        import onnxruntime

        if sample_rate not in (8000, 16000):
            raise ValueError(f'Unsupported sample rate for Silero VAD: {sample_rate}')

        self._session = onnxruntime.InferenceSession(
            model_path, providers=['CPUExecutionProvider']
        )
        inputs = {i.name: i for i in self._session.get_inputs()}
        if set(inputs) != {'input', 'sr', 'h', 'c'}:
            raise RuntimeError(f'Unsupported Silero VAD model inputs: {sorted(inputs)}')

        self._sample_rate = sample_rate
        self._window_size = 512 if sample_rate == 16000 else 256
        self._state_shape = (2, 1, inputs['h'].shape[2])
        self.reset()

    def reset(self):
        self._h = np.zeros(self._state_shape, dtype=np.float32)
        self._c = np.zeros(self._state_shape, dtype=np.float32)
        self._residual = np.zeros(0, dtype=np.float32)

    def predict(self, samples: np.ndarray) -> float:
        """
        :param samples: int16 PCM samples.
        :return: Mean speech probability (0-1) over the model windows completed
            by the audio. Leftover samples are carried over to the next call.
        """
        audio = np.concatenate([self._residual, samples.astype(np.float32) / 32768.0])
        num_windows = len(audio) // self._window_size
        self._residual = audio[num_windows * self._window_size :]

        probs = []
        for i in range(num_windows):
            window = audio[i * self._window_size : (i + 1) * self._window_size]
            out, self._h, self._c = self._session.run(
                None,
                {
                    'input': window[np.newaxis],
                    'sr': np.array(self._sample_rate, dtype=np.int64),
                    'h': self._h,
                    'c': self._c,
                },
            )
            probs.append(float(out[0][0]))

        return float(np.mean(probs)) if probs else 0.0


# vim:sw=4:ts=4:et:
