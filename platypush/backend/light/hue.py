import time

from threading import Thread

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.light import LightStatusChangeEvent


class LightHueBackend(Backend):
    """
    This backend will periodically check for the status of your configured
    Philips Hue light devices and trigger events when the status of a device
    (power, saturation, brightness or hue) changes.

    Triggers:

        * :class:`platypush.message.event.light.LightStatusChangeEvent` when the
            status of a lightbulb changes

    Requires:

        * The :class:`platypush.plugins.light.hue.LightHuePlugin` plugin to be
            active and configured.
    """

    _DEFAULT_POLL_SECONDS = 10

    def __init__(self, poll_seconds=_DEFAULT_POLL_SECONDS, *args, **kwargs):
        """
        :param poll_seconds: How often the backend will poll the Hue plugin for
            status updates. Default: 10 seconds
        :type poll_seconds: float
        """

        super().__init__(*args, **kwargs)
        self.poll_seconds = poll_seconds


    def _get_lights(self):
        plugin = get_plugin('light.hue')
        if not plugin:
            plugin = get_plugin('light.hue', reload=True)

        return plugin.get_lights().output

    def _listener(self):
        def _thread():
            lights = self._get_lights()

            while not self.should_stop():
                try:
                    lights_new = self._get_lights()

                    for light_id, light in lights_new.items():
                        event_args = {}
                        state = light.get('state')
                        prev_state = lights.get(light_id, {}).get('state', {})

                        if 'on' in state and state.get('on') != prev_state.get('on'):
                            event_args['on'] = state.get('on')
                        if 'bri' in state and state.get('bri') != prev_state.get('bri'):
                            event_args['bri'] = state.get('bri')
                        if 'sat' in state and state.get('sat') != prev_state.get('sat'):
                            event_args['sat'] = state.get('sat')
                        if 'hue' in state and state.get('hue') != prev_state.get('hue'):
                            event_args['hue'] = state.get('hue')
                        if 'ct' in state and state.get('ct') != prev_state.get('ct'):
                            event_args['ct'] = state.get('ct')

                        if event_args:
                            event_args['light_id'] = light_id
                            event_args['light_name'] = light.get('name')
                            self.bus.post(LightStatusChangeEvent(**event_args))

                    lights = lights_new
                except Exception as e:
                    self.logger.exception(e)
                finally:
                    time.sleep(self.poll_seconds)

        return _thread

    def run(self):
        super().run()

        while not self.should_stop():
            try:
                poll_thread = Thread(target=self._listener())
                poll_thread.start()
                poll_thread.join()
            except Exception as e:
                self.logger.exception(e)
                time.sleep(self.poll_seconds)

# vim:sw=4:ts=4:et:
