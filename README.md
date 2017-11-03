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

