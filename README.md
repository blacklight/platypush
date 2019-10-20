Platypush
=========

[![Build Status](https://travis-ci.org/BlackLight/platypush.svg?branch=master)](https://travis-ci.org/BlackLight/platypush)
[![Documentation Status](https://readthedocs.org/projects/platypush/badge/?version=latest)](https://platypush.readthedocs.io/en/latest/?badge=latest)
[![pip version](https://img.shields.io/pypi/v/platypush.svg?style=flat)](https://pypi.python.org/pypi/platypush/)

Advised read: [**Getting started with Platypush**](https://medium.com/@automationguru/automate-your-house-your-life-and-everything-else-around-with-platypush-dba1cd13e3f6) (Medium article).

Imagine Platypush as some kind of [IFTTT](https://ifttt.com) on steroids - or [Tasker](https://tasker.joaoapps.com/), or [Microsoft Flow](https://flow.microsoft.com), or [PushBullet](https://pushbullet.com) on steroids.
Platypush aims to turn any device in a smart hub that can control things, interact with cloud services and send messages to other devices. It's a general-purpose lightweight platform to process any request and run any logic triggered by custom events.

Imagine the ability of running any task you like, or automate any routine you like, on any of your devices. And the flexibility of executing actions through a cloud service, with the power of running them from your laptop, Raspberry Pi, smart home device or smartphone.

You can use Platypush to do things like:

- Control your smart home lights
- Control your favourite music player
- Interact with your voice assistant
- Get events from your Google or Facebook calendars
- Read data from your sensors and trigger custom events whenever they go above or below some custom thresholds
- Control the motors of your robot
- Send automated emails
- Synchronize the clipboards on your devices
- Control your smart switches
- Implement custom text-to-speech commands
- Build any kind of interaction with your Android device using Tasker
- Play local videos, YouTube videos and torrent links
- Get weather forecast for your location
- Build your own web dashboard with calendar, weather, news and music controls (basically, anything that has a Platypush web widget)
- ...and much more (basically, anything that comes with a [Platypush plugin](https://platypush.readthedocs.io/en/latest/plugins.html))

Imagine the ability of executing all the actions above through messages delivered through:

- A web interface
- A JSON-RPC API
- Raw TCP messages
- Web sockets
- [PushBullet](https://pushbullet.com)
- [Kafka](https://kafka.apache.org)
- [Redis](https://redis.io)
- [MQTT](https://mqtt.org)
- ...amd much more (basically, anything that comes with a [Platypush backend](https://platypush.readthedocs.io/en/latest/backends.html))

Imagine the ability of building custom event hooks to automatically trigger any actions:

- When your voice assistant recognizes some text
- When you start playing a new song
- When a new event is added to your calendar
- When a new article is published on your favourite feed
- When the weather conditions change
- When your press a [Flic button](https://flic.io) with a certain pattern
- When you receive a new push on your Pushbullet account
- When your GPS signal enters a certain area
- Whenever a new MIDI event is received (yes, you heard well :) )
- Whenever a sensor sends new data
- At a specific date or time
- ...and so on (basically, anything can send events that can be used to build hooks)

Imagine the ability of running the application, with lots of those bundled features, on any device that can comes with Python (_only compatible with version 3.5 and higher_). Platypush has been designed with performance in mind, it's been heavily tested on slower devices like Raspberry Pis, and it can run the web server features, multiple backends and plugins quite well even on a Raspberry Pi Zero - it's even been tested with some quite impressive performance on an older [Nokia N900](https://en.wikipedia.org/wiki/Nokia_N900), and of course you can run it on any laptop, desktop, server environment. It's been developed mainly with IoT in mind (and some of its features overlap with IoT frameworks like [Mozilla IoT](https://iot.mozilla.com) and [Android Things](https://developer.android.com/things/)), but nothing prevents you from automating any task on any device and environment.

To get started:

- [Wiki](https://github.com/BlackLight/platypush/wiki) for installation notes, quick start, examples and architecture reference
- [Read the docs](https://platypush.readthedocs.io/en/latest/) for a complete reference on the available plugins and backends
- [Medium articles](https://medium.com/tag/platypush/archive) that describe hands-on applications of platypush

