from unittest.mock import MagicMock, patch

from platypush.message.request import Request
from platypush.message.response import Response


class FakeExecutor:
    """
    A fake ThreadPoolExecutor that records submissions and can optionally
    run them synchronously so tests can observe side effects.
    """

    def __init__(self, run_sync=False):
        self.submitted = []
        self.run_sync = run_sync

    def submit(self, fn, *args, **kwargs):
        self.submitted.append((fn, args, kwargs))
        if self.run_sync:
            return fn(*args, **kwargs)

        future = MagicMock()
        return future


def test_async_request_submits_to_executor():
    fake = FakeExecutor(run_sync=True)
    req = Request(target='*', action='utils.get_context', args={})

    with (
        patch('platypush.message.request.get_request_executor', return_value=fake),
        patch('platypush.message.request.Config') as mock_config,
    ):
        mock_config.get.return_value = None
        mock_config.get_constants.return_value = {}
        with patch.object(req, '_send_response') as send_response:
            req.execute(_async=True)

    assert len(fake.submitted) == 1
    send_response.assert_called_once()


def test_sync_request_does_not_use_executor():
    fake = FakeExecutor(run_sync=True)
    req = Request(target='*', action='utils.get_context', args={})

    with (
        patch('platypush.message.request.get_request_executor', return_value=fake),
        patch('platypush.message.request.Config') as mock_config,
    ):
        mock_config.get.return_value = None
        mock_config.get_constants.return_value = {}
        with patch.object(req, '_send_response') as send_response:
            response = req.execute(_async=False)

    assert len(fake.submitted) == 0
    assert isinstance(response, Response)
    send_response.assert_called_once()
