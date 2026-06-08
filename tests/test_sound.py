import asyncio

import numpy as np

from platypush.plugins.sound._converters._base import AudioConverter
from platypush.plugins.sound._streams._player._resource import AudioResourcePlayer


class FakeAudioConverter(AudioConverter):
    @property
    def _input_format_args(self):
        return ()

    @property
    def _output_format_args(self):
        return ()


class FakeStdout:
    def __init__(self, chunks):
        self._chunks = list(chunks)

    async def read(self, *_):
        return self._chunks.pop(0)


class FakeFfmpeg:
    def __init__(self, chunks, returncode=0):
        self.returncode = returncode
        self.stdout = FakeStdout(chunks)

    async def wait(self):
        return self.returncode


class FakeStream:
    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(data)


def test_audio_resource_player_writes_end_padding_on_eof():
    player = AudioResourcePlayer(
        device=0,
        infile='test.wav',
        channels=1,
        volume=100,
        sample_rate=1000,
        dtype='int16',
        blocksize=100,
        end_padding=0.25,
    )

    stream = FakeStream()
    player.audio_stream = stream

    assert player._on_converter_eof(None) is False
    assert sum(len(write) for write in stream.writes) == 250
    assert all(write.dtype == np.dtype('int16') for write in stream.writes)
    assert all(np.all(write == 0) for write in stream.writes)


def test_audio_resource_player_does_not_pad_without_end_padding():
    player = AudioResourcePlayer(
        device=0,
        infile='test.wav',
        channels=1,
        volume=100,
        sample_rate=1000,
        dtype='int16',
        blocksize=100,
    )

    stream = FakeStream()
    player.audio_stream = stream

    assert player._on_converter_eof(None) is False
    assert stream.writes == []


def test_audio_converter_drains_stdout_after_ffmpeg_exits(monkeypatch):
    fake_ffmpeg = FakeFfmpeg([b'chunk-1', b'chunk-2', b''])

    async def fake_create_subprocess_exec(*_, **__):
        return fake_ffmpeg

    monkeypatch.setattr(
        asyncio,
        'create_subprocess_exec',
        fake_create_subprocess_exec,
    )

    converter = FakeAudioConverter(
        ffmpeg_bin='ffmpeg',
        sample_rate=44100,
        channels=1,
        volume=100,
        dtype='int16',
        chunk_size=1024,
    )
    converter._loop = object()

    asyncio.run(converter._audio_proxy(timeout=1))

    assert converter.read(timeout=0) == b'chunk-1'
    assert converter.read(timeout=0) == b'chunk-2'
    assert converter.read(timeout=0) == b''
