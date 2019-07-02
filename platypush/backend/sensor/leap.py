import time

from threading import Timer
from multiprocessing import Process

import Leap

from platypush.backend import Backend
from platypush.context import get_backend
from platypush.message.event.sensor.leap import LeapFrameEvent, \
    LeapFrameStartEvent, LeapFrameStopEvent, LeapConnectEvent, LeapDisconnectEvent


class SensorLeapBackend(Backend):
    """
    Backend for events generated using a Leap Motion device to track hands and
    gestures, https://www.leapmotion.com/

    Note that the default SDK is not compatible with Python 3. Follow the
    instructions on https://github.com/BlackLight/leap-sdk-python3 to build the
    Python 3 module.

    Also, you'll need the Leap driver and utils installed on your OS (follow
    instructions at https://www.leapmotion.com/setup/) and the `leapd` daemon
    running to recognize your controller.

    Requires:

        * The Redis backend enabled
        * The Leap Motion SDK compiled with Python 3 support, see my port at https://github.com:BlackLight/leap-sdk-python3.git
        * The `leapd` daemon to be running and your Leap Motion connected

    Triggers:

        * :class:`platypush.message.event.sensor.leap.LeapFrameEvent` when a new frame is received
        * :class:`platypush.message.event.sensor.leap.LeapFrameStartEvent` when a new sequence of frame starts
        * :class:`platypush.message.event.sensor.leap.LeapFrameStopEvent` when a sequence of frame stops
        * :class:`platypush.message.event.sensor.leap.LeapConnectEvent` when a Leap Motion device is connected
        * :class:`platypush.message.event.sensor.leap.LeapDisconnectEvent` when a Leap Motion device disconnects
    """

    _listener_proc = None

    def __init__(self,
                 position_ranges=None,
                 position_tolerance=0.0,  # Position variation tolerance in %
                 frames_throttle_secs=None,
                 *args, **kwargs):
        """
        :param position_ranges: It specifies how wide the hand space (x, y and z axes) should be in millimiters.

        Default::

            [
                [-300.0, 300.0],  # x axis
                [25.0, 600.0],    # y axis
                [-300.0, 300.0],  # z axis
            ]

        :type position_ranges: list[list[float]]

        :param position_tolerance: % of change between a frame and the next to really consider the next frame as a new one (default: 0)
        :type position_tolerance: float

        :param frames_throttle_secs: If set, the frame events will be throttled
            and pushed to the main queue at the specified rate. Good to set if
            you want to connect Leap Motion events to actions that have a lower
            throughput (the Leap Motion can send a lot of frames per second).
            Default: None (no throttling)
        :type frames_throttle_secs: float
        """

        super().__init__(*args, **kwargs)

        if position_ranges is None:
            position_ranges = [
                [-300.0, 300.0],  # x axis
                [25.0, 600.0],  # y axis
                [-300.0, 300.0],  # z axis
            ]

        self.position_ranges = position_ranges
        self.position_tolerance = position_tolerance
        self.frames_throttle_secs = frames_throttle_secs

    def run(self):
        super().run()

        def _listener_process():
            listener = LeapListener(position_ranges=self.position_ranges,
                                    position_tolerance=self.position_tolerance,
                                    frames_throttle_secs=self.frames_throttle_secs,
                                    logger=self.logger)

            controller = Leap.Controller()

            if not controller:
                raise RuntimeError('No Leap Motion controller found - is your ' +
                                'device connected and is leapd running?')

            controller.add_listener(listener)
            self.logger.info('Leap Motion backend initialized')

            while not self.should_stop():
                time.sleep(0.1)

        time.sleep(1)
        self._listener_proc = Process(target=_listener_process)
        self._listener_proc.start()
        self._listener_proc.join()


class LeapFuture(Timer):
    def __init__(self, seconds, listener, event):
        self.listener = listener
        self.event = event

        super().__init__(seconds, self._callback_wrapper())

    def _callback_wrapper(self):
        def _callback():
            self.listener._send_event(self.event)
        return _callback


class LeapListener(Leap.Listener):
    def __init__(self, position_ranges, position_tolerance, logger,
                 frames_throttle_secs=None):
        super().__init__()

        self.prev_frame = None
        self.position_ranges = position_ranges
        self.position_tolerance = position_tolerance
        self.frames_throttle_secs = frames_throttle_secs
        self.logger = logger
        self.running_future = None

    def _send_event(self, event):
        backend = get_backend('redis')
        if not backend:
            self.logger.warning('Redis backend not configured, I cannot propagate the following event: {}'.
                                format(event))
            return

        backend.send_message(event)

    def send_event(self, event):
        if self.frames_throttle_secs:
            if not self.running_future or not self.running_future.is_alive():
                self.running_future = LeapFuture(seconds=self.frames_throttle_secs,
                                                 listener=self, event=event)
                self.running_future.start()
        else:
            self._send_event(event)

    def on_init(self, controller):
        self.prev_frame = None
        self.logger.info('Leap controller listener initialized')

    def on_connect(self, controller):
        self.logger.info('Leap controller connected')
        self.prev_frame = None
        self.send_event(LeapConnectEvent())

    def on_disconnect(self, controller):
        self.logger.info('Leap controller disconnected')
        self.prev_frame = None
        self.send_event(LeapDisconnectEvent())

    def on_exit(self, controller):
        self.logger.info('Leap listener terminated')

    def on_frame(self, controller):
        frame = controller.frame()

        if len(frame.hands) > 0:
            hands = self._flatten_hands(frame)
            if hands:
                if not self.prev_frame:
                    self.send_event(LeapFrameStartEvent())
                self.send_event(LeapFrameEvent(hands=hands))
            self.prev_frame = frame
        else:
            if self.prev_frame:
                self.send_event(LeapFrameStopEvent())
            self.prev_frame = None

    def _flatten_hands(self, frame):
        return [
            {
                'confidence': hand.confidence,
                'direction': [hand.direction[0], hand.direction[1], hand.direction[2]],
                'id': hand.id,
                'is_left': hand.is_left,
                'is_right': hand.is_right,
                'palm_normal': [hand.palm_normal[0], hand.palm_normal[1], hand.palm_normal[2]],
                'palm_position': self._normalize_position(hand.palm_position),
                'palm_velocity': [hand.palm_velocity[0], hand.palm_velocity[1], hand.palm_velocity[2]],
                'palm_width': hand.palm_width,
                'sphere_center': [hand.sphere_center[0], hand.sphere_center[1], hand.sphere_center[2]],
                'sphere_radius': hand.sphere_radius,
                'stabilized_palm_position': self._normalize_position(hand.stabilized_palm_position),
                'time_visible': hand.time_visible,
                'wrist_position': self._normalize_position(hand.wrist_position),
            }
            for i, hand in enumerate(frame.hands)
            if hand.is_valid and (
                len(frame.hands) != len(self.prev_frame.hands) or
                self._position_changed(
                    old_position=self.prev_frame.hands[i].stabilized_palm_position,
                    new_position=hand.stabilized_palm_position)

                if self.prev_frame
                else True
            )
        ]

    def _normalize_position(self, position):
        # Normalize absolute position onto a hemisphere centered in (0,0)
        # having x_range = z_range = [-100, 100], y_range = [0, 100]

        return [
            self._scale_scalar(value=position[0], range=self.position_ranges[0], new_range=[-100.0, 100.0]),
            self._scale_scalar(value=position[1], range=self.position_ranges[1], new_range=[0.0, 100.0]),
            self._scale_scalar(value=position[2], range=self.position_ranges[2], new_range=[-100.0, 100.0]),
        ]

    @staticmethod
    def _scale_scalar(value, range, new_range):
        if value < range[0]:
            value=range[0]
        if value > range[1]:
            value=range[1]

        return ((new_range[1]-new_range[0])/(range[1]-range[0]))*(value-range[0]) + new_range[0]

    def _position_changed(self, old_position, new_position):
        return (
            abs(old_position[0]-new_position[0]) > self.position_tolerance or
            abs(old_position[1]-new_position[1]) > self.position_tolerance or
            abs(old_position[2]-new_position[2]) > self.position_tolerance)


# vim:sw=4:ts=4:et:
