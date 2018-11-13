"""
Controller for Plex content on a Chromecast device
"""

from pychromecast.controllers import BaseController


MESSAGE_TYPE = 'type'

TYPE_PLAY = "PLAY"
TYPE_PAUSE = "PAUSE"
TYPE_STOP = "STOP"

class PlexController(BaseController):
    """ Controller to interact with Plex namespace. """

    def __init__(self):
        super(PlexController, self).__init__(
            "urn:x-cast:plex", "9AC194DC")
        self.app_id="9AC194DC"
        self.namespace="urn:x-cast:plex"
        self.request_id = 0

    def stop(self):
        """ Send stop command. """
        self.namespace = "urn:x-cast:plex"
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_STOP})

    def pause(self):
        """ Send pause command. """
        self.namespace = "urn:x-cast:plex"
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PAUSE})

    def play(self):
        """ Send play command. """
        self.namespace = "urn:x-cast:plex"
        self.request_id += 1
        self.send_message({MESSAGE_TYPE: TYPE_PLAY})


    def play_media(self,item,server,medtype="LOAD"):
        def app_launched_callback():
                self.set_load(item,server,medtype)

        receiver_ctrl = self._socket_client.receiver_controller
        if receiver_ctrl.status.app_id != self.app_id:
            receiver_ctrl.launch_app(self.app_id,
                                     callback_function=app_launched_callback)

    def set_load(self,item,server,medtype="LOAD"):
        transient_token = server.query("/security/token?type=delegation&scope=all").attrib.get('token')
        playqueue = server.createPlayQueue(item).playQueueID
        self.request_id += 1
        address = server.url('').split(":")[1][2:]
        self.namespace="urn:x-cast:com.google.cast.media"
        msg = {
                "type": medtype,
                "requestId": self.request_id,
                "sessionId": "python_player",
                "autoplay": True,
                "currentTime": 0,
                "media":{
                        "contentId": item.key,
                        "streamType": "BUFFERED",
                        "contentType": "video",
                        "customData": {
                                "offset": 0,
                                "server": {
                                        "machineIdentifier": server.machineIdentifier,
                                        "transcoderVideo": True,
                                        "transcoderVideoRemuxOnly": False,
                                        "transcoderAudio": True,
                                        "version": "1.3.3.3148",
                                        "myPlexSubscription": False,
                                        "isVerifiedHostname": True,
                                        "protocol": "https",
                                        "address": address,
                                        "port": "32400",
                                        "accessToken": transient_token,
                                },
                                "user": {"username": server.myPlexUsername},
                                "containerKey": "/playQueues/{}?own=1&window=200".format(playqueue),
                        },
                }
        }
        self.send_message(msg, inc_session_id=True)

# vim:sw=4:ts=4:et:

