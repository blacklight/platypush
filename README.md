Platypush
=========

[![Build Status](https://travis-ci.org/BlackLight/platypush.svg?branch=master)](https://travis-ci.org/BlackLight/platypush)


Execute any command or custom complex logic on your devices, wherever they are, using your PushBullet account.

Installation
------------

```shell
pip install platypush
```

### Manual Installation

```shell
git clone https://github.com/BlackLight/platypush
cd platypush
python setup.py install
```

Configuration
-------------

Copy /etc/platypush/config.example.yaml to /etc/platypush/config.yaml (system-wise settings) or ~/.config/platypush/config.yaml (user-wise settings).

Edit the file to include:

### For the PushBullet backend

* Your PushBullet access token (create one [here](https://www.pushbullet.com/#settings/account));
* The name of the (virtual) PushBullet device used to listen for events (create one [here](https://www.pushbullet.com/#devices)).

### For the Apache Kafka backend

* The host and port of the Kafka installation
* The topic that will be used to deliver and process messages

### device_id

Each target device is identified by a unique device_id in the messages sent over your account. The device_id is the hostname by default, unless changed in config.yaml.

Shell interface
---------------

`platypush` installs `pusher`, a command-line tool to send PushBullet messages to the connected devices in the format used by platypush.

Some examples:

```shell
pusher --target laptop --action shell.exec --cmd "scp /home/user/photos/*.jpg backup_host:/mnt/hd/photos"
pusher --target raspberrypi --action music.mpd.play
```

The logic to execute is specified by the `--action` option, whose format is `package_name.method_name` (with method_name part of the package main class).

Available plugins
-----------------

* `platypush.plugins.shell`: The simplest and yet most versatile plugin. Executes a remote command on the host identified by the `--target` device_id. Example:

```shell
pusher --target laptop --action shell.exec --cmd "scp /home/user/photos/*.jpg backup_host:/mnt/hd/photos"
```

* `platypush.plugins.music.mpd`: Controls the playback on a mpd/mopidy music server. Requires the package `mpd2` on the target machine. Example:

```shell
pusher --target raspberry --action music.mpd.play
```

Configure the plugin through an entry like this in your `config.yaml`:

```yaml
music.mpd:
    host: your_mpd_host
    port: 6600
```

* `platypush.plugins.switch.wemo`: Controls a WeMo Switch smart switch device. Requires the package `ouimeaux` on the target machine. Example:

```shell
pusher --target raspberry --action switch.wemo.on
```

* `platypush.plugins.light.hue`: Controls a Philips Hue smart lights system. Requires the package `phue` on the target machine. Example:

```shell
pusher --target raspberry --action light.hue.scene --name "Sunset" --group "Living Room"
```

Writing your plugins
--------------------

Writing your own `platypush` plugin, that would execute your own custom logic whenever a bullet with your plugin name is received, is a very simple task.

1. Create your plugin directory under `platypush/plugins` (e.g. `light/batsignal`).

2. In the case above, `platypush.plugins.light.batsignal` will be your package name.

3. Create an `__init__.py` under `platypush/plugins/light/batsignal`.

4. If your module is `light/batsignal`, then its main class should be named `LightBatsignalPlugin`.

5. The configuration for your module will be read from a section named `light.batsignal` from your `config.yaml`. Its values will passed over the plugin constructor arguments.

The `__init__.py` will look like this:

```python
import batman

from platypush.message.response import Response

from .. import LightPlugin

class LightBatsignalPlugin(LightPlugin):
    def __init__(self, intensity=100):
        super().__init__()
        self.batsignal = batman.Batsignal(intensity)

    def on(self, urgent=False):
        if urgent:
            self.batsignal.notify_robin()

        self.batsignal.on()
        return Response(output='ok')

    def off(self):
        self.batsignal.off()
        return Response(output='ok')

    def toggle(self):
        self.batsignal.toggle()
        return Response(output='ok')

```

6. Rebuild and reinstall `platypush` if required and relaunch it.

7. Test your new plugin by sending some bullets to it:

```shell
pusher --target your_pc --action light.batsignal.on --urgent 1
```

Writing your backends
---------------------

You can also write your own backends, where a backend is nothing but a thread that listens for messages on a certain channel and pokes the main app whenever it receives one.

1. Create your backend directory under `platypush/backend` (e.g. `voicemail`)

2. In the case above, `platypush.backend.voicemail` will be your package name.

3. Create an `__init__.py` under `platypush/backend/voicemail`.

4. If your module is `voicemail`, then its main class should be named `VoicemailBackend`.

5. The configuration for your module will be read from a section named `backend.voicemail` from your `config.yaml`. Its values will be passed over the backend constructor arguments.

6. Implement the `run` method. Since a backend is a thread that polls for new messages on a channel, this will be the thread main method. `send_message` should call `self.on_message` at the end to post a new message to the application.

7. Implement the `send_message` method. This method will be called whenever the application needs to send a new message through `send_request` and `send_response`. You should never call `send_message` directly.

The `__init__.py` will look like this:

```python
from .. import Backend

class VoicemailBackend(Backend)
    def __init__(self, phone)
        super().__init__()
        self.phone = phone
        self.voicemail = Voicemail(...)

    def send_message(self, msg):
        self.voicemail.save_msg(msg)

    def run(self):
        while True:
            msg = self.voicemail.poll()
            self.on_message(msg)
```

