Runbullet
=========

Execute any command or custom complex logic on your devices, wherever they are, using your PushBullet account.

Installation
------------

```shell
pip install runbullet
```

Configuration
-------------

Copy /etc/runbullet/config.example.yaml to /etc/runbullet/config.yaml (system-wise settings) or ~/.config/runbullet/config.yaml (user-wise settings).

Edit the file to include:

* Your PushBullet access token (create one [here](https://www.pushbullet.com/#settings/account));
* The name of the (virtual) PushBullet device used to listen for events (create one [here](https://www.pushbullet.com/#devices)).

Each target device is identified by a unique device_id in the messages sent over your account. The device_id is the hostname by default, unless changed in config.yaml.

Testing
-------

`runbullet` installs `pusher`, a command-line tool to send PushBullet messages to the connected devices in the format used by runbullet.

Some examples:

```shell
echo '{"cmd":"scp /home/user/photos/*.jpg backup_host:/mnt/hd/photos"}' | pusher --target laptop --plugin shell
echo '{"play":true}' | pusher --target raspberrypi --plugin music.mpd
```

