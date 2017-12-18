from queue import Queue

class Bus(object):
    """ Main local bus where the daemon will listen for new messages """

    def __init__(self, on_msg=None):
        self.bus = Queue()
        self.on_msg = on_msg

    def post(self, msg):
        """ Sends a message to the bus """
        self.bus.put(msg)

    def loop_forever(self):
        """ Reads messages from the bus """
        if not self.on_msg: return

        while True:
            try:
                self.on_msg(self.bus.get())
            except KeyboardInterrupt:
                return

# vim:sw=4:ts=4:et:

