import time

import platypush.plugins.gpio.zeroborg.lib as ZeroBorg

no_msg_timeout = 0.37
last_msg = None
last_msg_timestamp = None
auto_mode = False

ZB = ZeroBorg.ZeroBorg()
ZB.Init()

while True:
    ZB.GetIrMessage()
    if ZB.HasNewIrMessage():
        message = ZB.GetIrMessage()
        print('Received message: {}'.format(message))

        last_msg = message
        last_msg_timestamp = time.time()

# vim:sw=4:ts=4:et:

