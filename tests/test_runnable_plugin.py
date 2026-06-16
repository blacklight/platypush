from platypush.plugins import RunnablePlugin


class BlockingRunnablePlugin(RunnablePlugin):
    def main(self):
        self.wait_stop()


def test_runnable_plugin_thread_is_daemon():
    plugin = BlockingRunnablePlugin()
    plugin.start()

    try:
        if not (plugin._thread is not None):
            raise AssertionError
        if not (plugin._thread.daemon):
            raise AssertionError
    finally:
        plugin.stop()
