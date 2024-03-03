import logging

from threading import Thread

from ._model import Command


class CommandBridge(Thread):
    """
    The command bridge is a thread that listens for commands on a command
    queue, proxies them to the Telegram service and returns the result back to
    the response queue.

    This is required because the Telegram service runs in a separate process -
    a requirement because of the Telegram bot API constraints, which requires
    the asyncio event loop to run in the main thread.
    """

    def __init__(self, service, *_, **__):
        from ._service import TelegramService

        super().__init__(name="telegram-service-bridge")
        self.logger = logging.getLogger("platypush:telegram:bridge")
        self._service: TelegramService = service

    def _exec(self, cmd: Command):
        try:
            result = self._service.exec(
                cmd.cmd, *cmd.args, **cmd.kwargs, timeout=cmd.timeout
            )
        except Exception as e:
            result = e

        self._service.result_queue.put_nowait((cmd, result))

    def run(self):
        super().run()

        while self._service.is_running():
            try:
                cmd = self._service.cmd_queue.get()
            except Exception as e:
                self.logger.warning("Error while reading command queue: %s", e)
                continue

            if cmd is None or cmd.is_end_of_service():
                break

            self._exec(cmd)


class ResultBridge(Thread):
    """
    The result bridge is a thread that listens for results on a result queue and
    proxies them to the response queue of the Telegram service.

    This is required because the Telegram service runs in a separate process -
    a requirement because of the Telegram bot API constraints, which requires
    the asyncio event loop to run in the main thread.
    """

    def __init__(self, plugin, *_, **__):
        from . import TelegramPlugin

        super().__init__(name="telegram-service-result-bridge")
        self.logger = logging.getLogger("platypush:telegram:result-bridge")
        self._plugin: TelegramPlugin = plugin

    def run(self):
        super().run()

        while not self._plugin.should_stop():
            try:
                ret = self._plugin.result_queue.get()
            except Exception as e:
                self.logger.warning("Error while reading result queue: %s", e)
                continue

            if not ret:
                break

            cmd, result = ret
            if cmd is None or cmd.is_end_of_service():
                break

            q = self._plugin.response_queues.get(cmd.id)
            if q:
                q.put_nowait(result)


# vim:sw=4:ts=4:et:
