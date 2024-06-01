import json
import os
from typing import Optional

from platypush.config import Config
from platypush.plugins import RunnablePlugin, action
from platypush.plugins.assistant import AssistantPlugin


class AssistantGooglePlugin(AssistantPlugin, RunnablePlugin):
    """
    Google Assistant plugin.

    This plugin allows you to run the Google Assistant _directly_ on your
    device. It requires you to have an audio microphone and a speaker connected
    to the device.

    If you have multiple sound devices, you can specify which one(s) to use for
    input and output through a ``~/.asoundrc`` configuration file like this:

        .. code-block:: text

            pcm.!default {
              type asym
               playback.pcm {
                 type plug
                 slave.pcm "hw:0,0"
               }
               capture.pcm {
                 type plug
                 slave.pcm "hw:1,0"
               }
            }

    You can use ``aplay -l`` and ``arecord -l`` to respectively list the
    detected audio output and input devices with their indices.

    If you are using PulseAudio instead of bare ALSA, then you can:

        1. Use the ``pavucontrol`` (GUI) tool to select the audio input and
           output devices and volumes for the assistant.
        2. Use a program like ``pamix`` (ncurses) or ``pamixer`` (CLI).
        3. Run the ``pactl list sources`` and ``pactl list sinks`` commands to
           respectively list the detected audio input and output devices. Take
           note of their name, and specify which ones the assistant should use
           by starting the application with the right ``PULSE_SOURCE`` and
           ``PULSE_SINK`` environment variables.

    .. warning:: The Google Assistant library used by this backend has
        been deprecated by Google:
        https://developers.google.com/assistant/sdk/reference/library/python/.
        This integration still works on all of my devices, but its future
        functionality is not guaranteed - Google may decide to turn off the
        API, the library may no longer be built against new architectures and
        it's unlikely to be updated.

    .. note:: Since the Google Assistant library hasn't been updated in several
        years, some of its dependencies are quite old and may break more recent
        Python installations. Please refer to the comments in the `manifest
        file
        <https://git.platypush.tech/platypush/platypush/src/branch/master/platypush/plugins/assistant/google/manifest.json>`_.
        for more information on how to install the required dependencies, if
        the automated ways fail.
    """

    _entity_name = 'Google Assistant'

    _default_credentials_files = (
        os.path.join(Config.get_workdir(), 'credentials', 'google', 'assistant.json'),
        os.path.join(
            os.path.expanduser('~/.config'), 'google-oauthlib-tool', 'credentials.json'
        ),
    )

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        device_model_id: str = 'Platypush',
        **kwargs,
    ):
        """
        :param credentials_file: Path to the Google OAuth credentials file.
            See
            https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample#generate_credentials
            for instructions to get your own credentials file.
            By default, it will search for the credentials file under:

                * ``~/.config/google-oauthlib-tool/credentials.json``: default
                  location supported by the Google Assistant library

                * ``<PLATYPUSH_WORKDIR>/credentials/google/assistant.json``:
                  recommended location, under the Platypush working directory.

        :param device_model_id: The device model ID that identifies the device
            where the assistant is running (default: Platypush). It can be a
            custom string.
        """
        super().__init__(**kwargs)
        self._credentials_file = credentials_file
        self.device_model_id = device_model_id
        self.credentials = None
        self._assistant = None
        self.logger.info('Initialized Google Assistant plugin')

    @property
    def credentials_file(self) -> str:
        if self._credentials_file:
            return os.path.abspath(os.path.expanduser(self._credentials_file))

        f = None
        for default_file in self._default_credentials_files:
            f = default_file
            if os.path.isfile(default_file):
                break

        assert f, 'No credentials_file provided and no default file found'
        return f

    @property
    def assistant(self):
        if not self._assistant:
            self.logger.warning('The assistant is not running')
            return

        return self._assistant

    def _process_event(self, event):
        from google.assistant.library.event import EventType, AlertType

        self.logger.info('Received assistant event: %s', event)

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self._on_conversation_start()
        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            if not event.args.get('with_follow_on_turn'):
                self._on_conversation_end()
        elif event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
            self._on_conversation_timeout()
        elif event.type == EventType.ON_NO_RESPONSE:
            self._on_no_response()
        elif (
            hasattr(EventType, 'ON_RENDER_RESPONSE')
            and event.type == EventType.ON_RENDER_RESPONSE
        ):
            self._on_response_render_start(event.args.get('text'))
        elif (
            hasattr(EventType, 'ON_RESPONDING_STARTED')
            and event.type == EventType.ON_RESPONDING_STARTED
            and event.args.get('is_error_response') is True
        ):
            self.logger.warning('Assistant response error: %s', json.dumps(event.args))
        elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            self._on_speech_recognized(event.args.get('text'))
        elif event.type == EventType.ON_ALERT_STARTED:
            if event.args.get('alert_type') == AlertType.ALARM:
                self._on_alarm_start()
            elif event.args.get('alert_type') == AlertType.TIMER:
                self._on_timer_start()
            else:
                self._on_alert_start()
        elif event.type == EventType.ON_ALERT_FINISHED:
            if event.args.get('alert_type') == AlertType.ALARM:
                self._on_alarm_end()
            elif event.args.get('alert_type') == AlertType.TIMER:
                self._on_timer_end()
            else:
                self._on_alert_end()
        elif event.type == EventType.ON_ASSISTANT_ERROR:
            if event.args.get('is_fatal'):
                raise RuntimeError(f'Fatal assistant error: {json.dumps(event.args)}')

            self.logger.warning('Assistant error: %s', json.dumps(event.args))
        elif event.type == EventType.ON_MUTED_CHANGED:
            self._on_mute_changed(event.args.get('is_muted', False))

    @action
    def start_conversation(self, *_, **__):
        """
        Programmatically start a conversation with the assistant
        """
        if self.assistant:
            self.assistant.start_conversation()

    def _stop_conversation(self, *_, **__):
        """
        Programmatically stop a running conversation with the assistant
        """
        if self.assistant:
            self.assistant.stop_conversation()

    @action
    def mute(self, *_, **__):
        """
        Mute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=True``.
        """
        self.set_mic_mute(muted=True)

    @action
    def unmute(self, *_, **__):
        """
        Unmute the microphone. Alias for :meth:`.set_mic_mute` with
        ``muted=False``.
        """
        self.set_mic_mute(muted=False)

    @action
    def set_mic_mute(self, muted: bool):
        """
        Programmatically mute/unmute the microphone.

        :param muted: Set to True or False.
        """
        if self.assistant:
            self.assistant.set_mic_mute(muted)

            if muted:
                self._on_mute()
            else:
                self._on_unmute()

    @action
    def toggle_mute(self, *_, **__):
        """
        Toggle the mic mute state.
        """
        self.set_mic_mute(muted=not self._is_muted)

    @action
    def toggle_mic_mute(self):
        """
        Deprecated alias for :meth:`.toggle_mute`.
        """
        return self.toggle_mute()

    @action
    def send_text_query(self, *_, query: str, **__):
        """
        Send a text query to the assistant.

        This is equivalent to saying something to the assistant.

        :param query: Query to be sent.
        """
        if self.assistant:
            self.assistant.send_text_query(query)

    def main(self):
        import google.oauth2.credentials
        from google.assistant.library import Assistant

        last_sleep = 0

        while not self.should_stop():
            try:
                with open(self.credentials_file, 'r') as f:
                    self.credentials = google.oauth2.credentials.Credentials(
                        token=None, **json.load(f)
                    )
            except Exception as e:
                self.logger.error(
                    'Error while loading Google Assistant credentials: %s', e
                )
                self.logger.info(
                    'Please follow the instructions at '
                    'https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample'
                    '#generate_credentials to get your own credentials file'
                )
                self.logger.exception(e)
                break

            try:
                with Assistant(
                    self.credentials, self.device_model_id
                ) as self._assistant:
                    self.publish_entities([self])
                    for event in self._assistant.start():
                        last_sleep = 0

                        if not self.is_detecting():
                            self.logger.info(
                                'Assistant event received but detection is currently paused'
                            )
                            continue

                        self._process_event(event)
            except Exception as e:
                self.logger.exception(e)
                sleep_secs = min(60, max(5, last_sleep * 2))
                self.logger.warning(
                    'Restarting the assistant in %d seconds after an unrecoverable error',
                    sleep_secs,
                )

                self.wait_stop(sleep_secs)
                last_sleep = sleep_secs
                continue

    def stop(self):
        try:
            self.stop_conversation()
        except RuntimeError:
            pass

        if self._assistant:
            del self._assistant
            self._assistant = None

        super().stop()


# vim:sw=4:ts=4:et:
