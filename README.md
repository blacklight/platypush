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

Check `requirements.txt` for any extra dependencies you may want to install depending on your configuration. You can also install all the dependencies (may take some time on slow machines) by running `pip install -r requirements.txt`.

After configuring the server, start it by simply running `platypush`.

Check [our wiki](https://github.com/BlackLight/platypush/wiki) for any additional info about [configuration](https://github.com/BlackLight/platypush/wiki/Configuration) together with examples, use the shell interface, or write your own plugins and backend.

