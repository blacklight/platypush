Platypush
=========

[![Build Status](https://travis-ci.org/BlackLight/platypush.svg?branch=master)](https://travis-ci.org/BlackLight/platypush)


Execute any command or custom complex logic on your devices, wherever they are, using PushBullet, Apache Kafka, or any backend.

Platypush aims to be a general-purpose middleware infrastructure to process any request and run any logic triggered by custom events on a generic network of hosts.

Its development is mainly driven by the necessity of a lightweight infrastructure for running generic triggers and actions in a virtual network, generalizing a bit the idea of an Android app like Tasker or a web service like IFTTT or Microsoft Flow, and turning it into something that anybody can run on their own devices. It's actively being tested on RaspberryPi devices and it has interesting applications when it comes to home automation and IoT, but it should be generic enough to solve most of the automation and information delivery issues in a distributed network.

Architecture
------------

The base components are:

* __Messages__: _requests_, _responses_ or _events_. The main difference between a request and an event is that the former specifies an explicit action to be executed through a _plugin_ (and the sender will usually wait for a _response_), while an event only notifies that something happened on a connected data source and can either be ignored or trigger some custom actions specified in the configuration.

* The __Bus__: An internal queue where all the other components exchange messages.

* __Backends__: Components that poll other data sources (a local queue, a remote websocket, a Kafka instance, or even a vocal assistant, a programmable button or a sensor) and post either requests or events on the bus when something happens on the data source. Some of them can have a full-duplex integration with the bus, i.e. post requests and events on the bus as they come and deliver responses from the bus back to the sender (examples: PushBullet, Apache Kafka, sockets), while some are pure data sources that will only post events on the bus (examples: sensors, buttons, vocal assistants).

* __Plugins__: Configurable components which expose _actions_ that can be triggered by requests or events. Examples: smart lights, music controls, YouTube or torrentcast features, text-to-speech, generic shell commands, etc.). They would usually deliver output and errors as responses on the bus.

* __Procedures__: Pre-configured lists of actions that can be triggered by requests or events.

* Event __Hooks__: Pre-configured actions that will be executed when certain events are processed. They include:
    * A _condition_, which can be fuzzly compared against an event. The matching logic will also return a _match score_ if the condition is met. The score is a function of the number of atomic matches (string tokens, scalars, key-values etc.) in the condition that are satisfied by a certain event. If multiple hooks are satisfied by a certain event, the algorithm will only run the ones with the highest score.
    * One or more _actions_ to be executed in case of event match (e.g. "turn on the lights", "send a Messenger message to my s.o.", "turn on the heating", "play the radio" etc.)

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

Check `all_requirements.txt` for any extra dependencies you may want to install depending on your configuration. You can also install all the dependencies (may take some time on slow machines) by running `pip install -r all_requirements.txt`.

After configuring the server, start it by simply running `platypush`.

Configuration
-------------

Copy `/etc/platypush/config.example.yaml` to `/etc/platypush/config.yaml` (system-wise settings) or `~/.config/platypush/config.yaml` (user-wise settings).

Some configuration snippets:

### device_id

Each target device is identified by a unique device_id in the messages sent over your account. The device_id is the hostname by default, unless a different value is set in config.yaml at the root level.

### Backends

Platypush comes by default with a [PushBullet](https://www.pushbullet.com/) backend, an [Apache Kafka](https://kafka.apache.org/) backend, and a (quite unstable) local backend based on fifos. Backend configurations start with `backend.` in the `config.yaml`.

#### PushBullet configuration

You will need:

* Your PushBullet access token (create one [here](https://www.pushbullet.com/#settings/account));
* The name of the (virtual) PushBullet device used to listen for events (create one [here](https://www.pushbullet.com/#devices)).

```yaml
backend.pushbullet:
    token: PUSHBULLET_TOKEN
    device: platypush
```

#### Apache Kafka configuration

This would be a sample snippet for an Apache Kafka configuration:

```yaml
backend.kafka:
    pusher: True   # Default pusher backend
    server: server:9092  # Kafka server and port
    topic: platypush  # Topic prefix. Note: platypush will create a topic for each device named <topic>.<device_id>
```

Note: specifying `pusher: True` on a backend configuration means that that backend will be the default one used to deliver requests or events to other nodes through the `pusher` script, if no `--backend` option is passed.

#### Local backend configuration

```yaml
backend.local:
    request_fifo: /tmp/platypush-requests.fifo
    response_fifo: /tmp/platypush-responses.fifo
```

#### Google Assistant configuration

Follow the steps on the [Google Assistant SDK](https://github.com/googlesamples/assistant-sdk-python/tree/master/google-assistant-sdk) page and get the assistant sample running on your machine.

Afterwards, you can enable custom speech-triggered actions on Platypush by just enabling the assistant backend:

```yaml
backend.assistant.google:
    disabled: False
```

#### Flic buttons configuration

[Flic buttons](https://flic.io/) are a quite cool and useful accessory. You can pair them with your phone over Bluetooth and they can trigger anything on your device - play music on Spotify, start a timer, trigger a Tasker task, snooze alarms, trigger fake phone calls...

A [beta SDK](https://github.com/50ButtonsEach/fliclib-linux-hci) is available as well that allows you to pair the buttons to any bluetooth device, not necessarily running the Flic app.

Install the SDK and run the `flicd` server on your machine. You can then enable the Flic plugin:

```yaml
backend.button.flic:
    server: localhost

```

By the way, the Flic app only supports a maximum of three events per button - short press, long press and double press. With the Platypush plugin you can trigger countless actions by configuring multiple combinations of short and long presses - provided that you can remember them.

### Plugins

A couple of plugins are available out of the box with platypush under `plugins/`. Some of them may require extras Python or system dependencies. Some of the available plugins include:

#### MPD/Mopidy support

[MPD](https://musicpd.org/) is an application that allows to manage and play your music collection through a scalable client/server model. You can have your server running on a machine with a hard drive stuffed with mp3s, and access your collection from anywhere using a big family of compatible command line, graphical, web or mobile clients. [Mopidy](https://www.mopidy.com/) is an evolution of MPD that allows you to access music content from multiple sources through a wide set of plugins - e.g. Spotify, SoundCloud, Deezer, Pandora, TuneIn, Google Music.

Platypush can be a client for your MPD/Mopidy music server, allowing you to search for music, control your queue and the playback upon requests or events.

Configuration:

```yaml
music.mpd:
    host: localhost
    port: 6600
```

#### Video and media support

Platypush comes with support for video media, including YouTube, local media and torrents (requires [torrentcast](https://www.npmjs.com/package/torrentcast)). It's quite handy to turn a RaspberryPi into a full-blown media server or a Chromecast on steroids, voice controls included.

```yaml
video.omxplayer:
    args:
        - -o
        - alsa  # or hdmi
        # ... any other default options for OMXPlayer

video.torrentcast:
    server: localhost
    port: 9090
```

#### Philips Hue lights support

Control your [Philips Hue](https://www2.meethue.com/en-us) lights with custom requests and events triggered by your devices.

```yaml
light.hue:
    bridge: bridge_name_or_ip
    # If no lights or groups to actions are specified in
    # the action or in the default configuration, all the
    # lights will be targeted.

    lights:
        - Hall
        - Living Room Left
        - Living Room Right
        - Garage
    groups:
        - Bedroom
        - Kitchen
```

#### Belkin WeMo Switch

The [WeMo Switch](http://www.belkin.com/us/p/P-F7C027/) is smart Wi-Fi controlled switch that can automate the control of any electric appliance - fridges, lights, coffee machines...

The Platypush plugin requires `ouimeaux` and will work with no configuration needed.

#### Text-to-Speech support

If `mplayer` is installed, you can trigger a machine to say custom phrases in any language through the `tts` plugin. Quite cool if you want to let your RaspberryPi to automatically read you out loud the news or when you get a notification on your phone.

```yaml
tts:
    lang: en-gb  # Default language
```

#### Shell plugin

You can also run custom shell commands on the target machine through the `shell` plugin, that requires (for now) no configuration.

### Procedures

Procedures are sequences of actions that will be executed in parallel or in series (*TODO*) by Platypush. Useful to refactor sequences of repeated actions in your requests or event hooks. Their configuration names start with `procedure.`.

```yaml
procedure.at_home:
    -
        action: tts.say
        args:
            phrase: Welcome home, YOUR_NAME
    -
        action: light.hue.on
    -
        action: switch.wemo.on
        args:
            device: Heater
    -
        action: music.mpd.play
        args:
            resource: spotify:user:you:playlist:your_favourite_playlist
    -
        action: shell.exec
        args:
            cmd: './bin/sensors_report.sh'
```

### Event Hooks

Event hooks are one of the most powerful features of Platypush. They are the equivalent of a profile in Tasker, or a recipe in IFTTT. They link events received on the main bus to actions that can be triggered on the local or on a remote node. Events will usually be ignored unless you configured a hook for handling them. Their configuration names start with `event.hook.`.

Some examples:

```yaml
event.hook.AssistantConversationStarted:
    if:
        type: platypush.message.event.assistant.ConversationStartEvent
    then:
        -
            action: shell.exec
            args:
                cmd: 'aplay /usr/share/sounds/start.wav'


event.hook.LightsSceneAssistantCommand:
    if:
        type: platypush.message.event.assistant.SpeechRecognizedEvent
        # Note: regex support (still quite experimental though) and support for
        # parsing context variables out of the trigger event, that can be used
        # in the executed actions. Context variables names start with $
        # (escape it with \ if you want to use the literal symbol instead).
        # The context variables already include the variables of the source event,
        # meaning that you can use $phrase as well in your action for this example.
        phrase: "set (the)? scene on $name"
    then:
        -
            action: light.hue.scene
            args:
                # If you said "set the scene on sunset", $name=sunset
                name: $name


event.hook.NextSongFlicButton:
    if:
        type: platypush.message.event.button.flic.FlicButtonEvent
        btn_addr: 00:11:22:33:44:55
        sequence:
            # Lists are supported too
            - ShortPressEvent
            - LongPressEvent
    then:
        -
            action: music.mpd.next
        # You can also specify multiple actions
        -
            action: media.ctrl.forward
        # Or procedures
        -
            action: procedure.your_proc
```

Shell interface
---------------

`platypush` installs `pusher`, a command-line tool to send PushBullet messages to the connected devices in the format used by platypush.

Some examples:

```shell
pusher --target laptop --action shell.exec --cmd "scp /home/user/photos/*.jpg backup_host:/mnt/hd/photos"
pusher --target raspberrypi --action music.mpd.play
```

The logic to execute is specified by the `--action` option, whose format is `package_name.method_name` (with method_name part of the package main class).

Sample requests through Pusher
------------------------------

* `platypush.plugins.shell`:

```shell
pusher --target laptop --action shell.exec --cmd "scp /home/user/photos/*.jpg backup_host:/mnt/hd/photos"
```

* `platypush.plugins.music.mpd`:

```shell
pusher --target raspberry --action music.mpd.play
```

* `platypush.plugins.switch.wemo`:

```shell
pusher --target raspberry --action switch.wemo.on
```

* `platypush.plugins.light.hue`:

```shell
pusher --target raspberry --action light.hue.scene --name "Sunset" --group "Living Room"
```

* `procedure`:

```shell
pusher --target raspberry --action procedure.at_home
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

