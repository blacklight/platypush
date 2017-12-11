Platypush
=========

Execute any command or custom complex logic on your devices, wherever they are, using your PushBullet account.

Installation
------------

```shell
pip install platypush
```

### Manual Installation

```shell
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

### For the local socket backend

* The name of the local FIFO that will be used to deliver and process messages

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

5. The configuration for your module will be read from a section named `light.batsignal` from your `config.yaml`, the attributes are accessible in your class in `self.config`.

The `__init__.py` will look like this:

```python
import batman

from .. import LightPlugin

class LightBatsignalPlugin(LightPlugin):
    def _init(self):
        self.batsignal = batman.Batsignal(self.config['intensity'])

    def on(self, urgent=False):
        if urgent:
            self.batsignal.notify_robin()

        self.batsignal.on()

    def off(self):
        self.batsignal.off()

    def toggle(self):
        self.batsignal.toggle()

    def status(self):
        return [self.batsignal.status().stdout, self.batsignal.status().stderr]
```

6. It's a good practice to define a `status` method in your plugin, which returns a 2-items list like `[output, error]`.

7. Rebuild and reinstall `platypush` if required and relaunch it.

8. Test your new plugin by sending some bullets to it:

```shell
pusher --target your_pc --action light.batsignal.on --urgent 1
```

