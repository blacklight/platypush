from platypush.plugins import RunnablePlugin


class BlockingRunnablePlugin(RunnablePlugin):
    def main(self):
        self.wait_stop()


def test_runnable_plugin_thread_is_daemon():
    plugin = BlockingRunnablePlugin()
    plugin.start()

    try:
        assert plugin._thread is not None
        assert plugin._thread.daemon
    finally:
        plugin.stop()
