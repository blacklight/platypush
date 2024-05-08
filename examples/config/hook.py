# A more versatile way to define event hooks than the YAML format of `config.yaml` is through native Python scripts.
# You can define hooks as simple Python functions that use the `platypush.event.hook.hook` decorator to specify on
# which event type they should be called, and optionally on which event attribute values.
#
# Event hooks should be stored in Python files under `~/.config/platypush/scripts`. All the functions that use the
# @when decorator will automatically be discovered and imported as event hooks into the platform at runtime.

# `run` is a utility function that runs a request by name (e.g. `light.hue.on`).
from platypush import when, run

# Event types that you want to react to
from platypush.message.event.assistant import (
    ConversationStartEvent,
    SpeechRecognizedEvent,
)


@when(SpeechRecognizedEvent, phrase='play ${title} by ${artist}')
def on_music_play_command(event, title=None, artist=None, **context):
    """
    This function will be executed when a SpeechRecognizedEvent with `phrase="play the music"` is triggered.
    `event` contains the event object and `context` any key-value info from the running context.
    Note that in this specific case we can leverage the token-extraction feature of SpeechRecognizedEvent through
    ${} that operates on regex-like principles to extract any text that matches the pattern into context variables.
    """
    results = run(
        'music.mpd.search',
        filter={
            'artist': artist,
            'title': title,
        },
    )

    if results:
        run('music.mpd.play', results[0]['file'])
    else:
        run('tts.say', "I can't find any music matching your query")


@when(ConversationStartEvent)
def on_conversation_start(event, **context):
    """
    A simple hook that gets invoked when a new conversation starts with a voice assistant and simply pauses the music
    to make sure that your speech is properly detected.
    """
    run('music.mpd.pause_if_playing')
