# Chromecast Channel Protocol

This directory contains the vendored Google Cast channel protocol buffer
(vendored under the Apache 2.0 / BSD-style license) and the generated Python
module used by the Chromecast receiver.

## Regenerating `cast_channel_pb2.py`

```bash
protoc --python_out=. cast_channel.proto
```

Run the command from this directory. The generated module is checked into the
repository so the receiver works without a `protoc` build step at install time.
