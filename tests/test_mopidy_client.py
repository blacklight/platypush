import threading
import time
from queue import Queue
from unittest.mock import MagicMock

import pytest

from platypush.plugins.music.mopidy import MusicMopidyPlugin
from platypush.plugins.music.mopidy._client import MopidyClient
from platypush.plugins.music.mopidy._conf import MopidyConfig
from platypush.plugins.music.mopidy._status import MopidyStatus
from platypush.plugins.music.mopidy._sync import PlaylistSync


def _client(tasks=None):
    return MopidyClient(
        config=MopidyConfig(),
        status=MopidyStatus(),
        stop_event=threading.Event(),
        playlist_sync=PlaylistSync(),
        tasks=tasks if tasks is not None else {},
    )


def _wait_for_refresh(client, timeout=2):
    start = time.time()
    while client._refresh_status_thread and time.time() - start < timeout:
        time.sleep(0.01)


def test_task_cleanup_after_response():
    client = _client()
    task = client.make_task('core.playback.get_state')
    assert task.id in client._tasks

    client._on_msg('{"id": 1, "result": "playing"}')
    results = list(client.gather(task, timeout=1))

    assert results == ['playing']
    assert not client._tasks


def test_task_cleanup_after_timeout():
    client = _client()
    task = client.make_task('core.playback.get_state')
    assert task.id in client._tasks

    with pytest.raises(TimeoutError):
        list(client.gather(task, timeout=0.1))

    assert not client._tasks


def test_pending_task_failure_on_close():
    client = _client()
    task = client.make_task('core.playback.get_state')
    result = Queue()

    def gather_task():
        try:
            list(client.gather(task, timeout=2))
            result.put(None)
        except Exception as e:
            result.put(e)

    thread = threading.Thread(target=gather_task)
    thread.start()
    time.sleep(0.05)
    client._on_close()
    thread.join(timeout=2)

    exc = result.get(timeout=1)
    assert exc is not None
    assert not client._tasks


def test_reconnect_does_not_misroute_old_task_ids():
    tasks = {}
    client1 = _client(tasks=tasks)
    old_task = client1.make_task('core.playback.get_state')
    assert old_task.id in tasks
    assert old_task.generation == client1._client_generation

    client2 = _client(tasks=tasks)
    assert client2._client_generation != client1._client_generation

    # A response with the same numeric ID as an old task should not satisfy it.
    client2._on_msg('{"id": 1, "result": "stale"}')
    assert old_task.response is None
    assert old_task.id not in tasks

    # The new client can safely reuse the same numeric ID.
    new_task = client2.make_task('core.playback.get_state')
    assert new_task.id == old_task.id
    assert new_task.generation == client2._client_generation

    client2._on_msg('{"id": 1, "result": "fresh"}')
    results = list(client2.gather(new_task, timeout=1))
    assert results == ['fresh']
    assert not tasks


def test_reconcile_tasks_on_reconnect():
    plugin = MusicMopidyPlugin(disable_monitor=True)
    client = _client(tasks=plugin._tasks)
    plugin._client = client

    client.make_task('core.playback.get_state')
    assert len(plugin._tasks) == 1

    plugin._reconcile_tasks()
    assert not plugin._tasks


def test_refresh_status_debounce():
    client = _client()
    client._post_event = MagicMock()
    client.exec = MagicMock(
        return_value=[
            False,
            False,
            False,
            False,
            None,
            'stopped',
            50,
            0,
        ]
    )

    for _ in range(5):
        client._refresh_status()
        time.sleep(0.01)

    _wait_for_refresh(client)
    assert client.exec.call_count <= 1


def test_refresh_tracklist_bypasses_non_track_debounce():
    client = _client()
    client._post_event = MagicMock()
    client.exec = MagicMock(
        return_value=[
            False,
            False,
            False,
            False,
            None,
            'stopped',
            50,
            0,
            [],
        ]
    )

    client._refresh_status(with_tracks=True)
    _wait_for_refresh(client)
    assert client.exec.call_count == 1

    # A non-track refresh immediately after should be debounced.
    client._refresh_status(with_tracks=False)
    _wait_for_refresh(client)
    assert client.exec.call_count == 1

    # A tracklist refresh should still be allowed.
    client._refresh_status(with_tracks=True)
    _wait_for_refresh(client)
    assert client.exec.call_count == 2


def test_refresh_status_tracklist_index_fast_path():
    client = _client()
    client._post_event = MagicMock()
    ret = [
        False,
        False,
        False,
        False,
        {'uri': 'track://1', 'tlid': 123},
        'playing',
        50,
        0,
        [{'uri': 'track://1', 'tlid': 123}],
    ]
    client.exec = MagicMock(return_value=ret)

    client.refresh_status(with_tracks=True)

    # Only one batch of requests should have been sent; the index lookup was
    # avoided because the tracklist was already in the response.
    assert client.exec.call_count == 1
    assert client._status.playing_pos == 0


def test_cleanup_stale_tasks():
    client = _client()
    task = client.make_task('core.playback.get_state')
    task.created_at = time.time() - 300

    assert len(client._tasks) == 1
    removed = client._cleanup_stale_tasks(max_age=120)
    assert removed == 1
    assert not client._tasks
