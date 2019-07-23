import os
import tempfile

from flask import Response, Blueprint, request

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request

sound = Blueprint('sound', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    sound,
]


# Generates the .wav file header for a given set of samples and specs
# noinspection PyRedundantParentheses
def gen_header(sample_rate, sample_width, channels):
    datasize = int(2000 * 1e6)                                               # Arbitrary data size for streaming
    o = bytes("RIFF", ' ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4, 'little')                               # (4byte) File size in bytes
    o += bytes("WAVE", 'ascii')                                              # (4byte) File type
    o += bytes("fmt ", 'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4, 'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2, 'little')                                           # (2byte) Format type (1 - PCM)
    o += channels.to_bytes(2, 'little')                                      # (2byte)
    o += sample_rate.to_bytes(4,  'little')                                  # (4byte)
    o += (sample_rate * channels * sample_width // 8).to_bytes(4, 'little')  # (4byte)
    o += (channels * sample_width // 8).to_bytes(2, 'little')                # (2byte)
    o += sample_width.to_bytes(2, 'little')                                  # (2byte)
    o += bytes("data", 'ascii')                                              # (4byte) Data Chunk Marker
    o += datasize.to_bytes(4, 'little')                                      # (4byte) Data size in bytes
    return o


def audio_feed(device, fifo, sample_rate, blocksize, latency, channels):
    send_request(action='sound.stream_recording', device=device, sample_rate=sample_rate,
                 dtype='int16', fifo=fifo, blocksize=blocksize, latency=latency,
                 channels=channels)

    try:
        with open(fifo, 'rb') as f:
            send_header = True

            while True:
                audio = f.read(blocksize)

                if audio:
                    if send_header:
                        audio = gen_header(sample_rate=sample_rate, sample_width=16, channels=channels) + audio
                        send_header = False

                    yield audio
    finally:
        send_request(action='sound.stop_recording')


@sound.route('/sound/stream', methods=['GET'])
@authenticate()
def get_sound_feed():
    device = request.args.get('device')
    sample_rate = request.args.get('sample_rate', 44100)
    blocksize = request.args.get('blocksize', 512)
    latency = request.args.get('latency', 0)
    channels = request.args.get('channels', 1)
    fifo = request.args.get('fifo', os.path.join(tempfile.gettempdir(), 'inputstream'))

    return Response(audio_feed(device=device, fifo=fifo, sample_rate=sample_rate,
                               blocksize=blocksize, latency=latency, channels=channels),
                    mimetype='audio/x-wav;codec=pcm')


# vim:sw=4:ts=4:et:
