import json
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.todoist import NewItemEvent, RemovedItemEvent, ModifiedItemEvent, CheckedItemEvent, \
    ItemContentChangeEvent, TodoistSyncRequiredEvent

from platypush.plugins.todoist import TodoistPlugin


class TodoistBackend(Backend):
    """
    This backend listens for events on a remote Todoist account.

    Requires:

        * **todoist-python** (``pip install todoist-python``)

    Triggers:

        * :class:`platypush.message.event.todoist.NewItemEvent` when a new item is created.
        * :class:`platypush.message.event.todoist.RemovedItemEvent` when an item is removed.
        * :class:`platypush.message.event.todoist.CheckedItemEvent` when an item is checked.
        * :class:`platypush.message.event.todoist.ItemContentChangeEvent` when the content of an item is changed.
        * :class:`platypush.message.event.todoist.ModifiedItemEvent` when an item is changed and the change
            doesn't fall into the categories above.
        * :class:`platypush.message.event.todoist.TodoistSyncRequiredEvent` when an update has occurred that doesn't
            fall into the categories above and a sync is required to get up-to-date.

    """

    def __init__(self, api_token: str = None, **kwargs):
        super().__init__(**kwargs)
        self._plugin: TodoistPlugin = get_plugin('todoist')

        if not api_token:
            assert self._plugin and self._plugin.api_token, 'No api_token specified either on Todoist backend or plugin'
            self.api_token = self._plugin.api_token
        else:
            self.api_token = api_token

        self.url = self._plugin.get_user().output['websocket_url']
        self._ws = None
        self._connected = False
        self._todoist_initialized = False

        self._items = {}
        self._event_handled = False

    def _on_msg(self):
        def hndl(*args):
            msg = args[1] if len(args) > 1 else args[0]
            msg = json.loads(msg)
            if msg.get('type') == 'sync_needed':
                self._refresh_all()

        return hndl

    def _retry_hndl(self):
        self._ws = None
        self.logger.warning('Todoist websocket connection closed')
        self._connected = False

        while not self._connected:
            self._connect()
            time.sleep(10)

    def _on_error(self):
        def hndl(*args):
            error = args[1] if len(args) > 1 else args[0]
            self.logger.warning('Todoist websocket error: {}'.format(error))
            self._retry_hndl()

        return hndl

    def _on_close(self):
        def hndl(*_):
            self.logger.info('Todoist websocket closed')
            self._retry_hndl()

        return hndl

    def _on_open(self):
        # noinspection PyUnusedLocal
        def hndl(ws):
            self._connected = True
            self.logger.info('Todoist websocket connected')

            if not self._todoist_initialized:
                self._refresh_all()
                self._todoist_initialized = True

        return hndl

    def _connect(self):
        import websocket

        if not self._ws:
            self._ws = websocket.WebSocketApp(self.url,
                                              on_message=self._on_msg(),
                                              on_error=self._on_error(),
                                              on_close=self._on_close())

    def _refresh_items(self):
        new_items = {
            i['id']: i
            for i in self._plugin.get_items().output
        }

        if self._todoist_initialized:
            for id, item in new_items.items():
                if id not in self._items.keys():
                    self._event_handled = True
                    self.bus.post(NewItemEvent(item))

            for id, item in self._items.items():
                if id not in new_items.keys():
                    self._event_handled = True
                    self.bus.post(RemovedItemEvent(item))
                elif new_items[id] != item:
                    if new_items[id]['checked'] != item['checked']:
                        self._event_handled = True
                        self.bus.post(CheckedItemEvent(new_items[id]))
                    elif new_items[id]['is_deleted'] != item['is_deleted']:
                        self._event_handled = True
                        self.bus.post(RemovedItemEvent(new_items[id]))
                    elif new_items[id]['content'] != item['content']:
                        self._event_handled = True
                        self.bus.post(ItemContentChangeEvent(new_items[id]))
                    else:
                        self._event_handled = True
                        self.bus.post(ModifiedItemEvent(new_items[id]))

        self._items = new_items

    def _refresh_all(self):
        self._event_handled = False
        self._plugin.sync()
        self._refresh_items()

        if not self._event_handled:
            self.bus.post(TodoistSyncRequiredEvent())

    def run(self):
        super().run()
        self.logger.info('Started Todoist backend')

        self._connect()
        self._ws.on_open = self._on_open()
        self._ws.run_forever()


# vim:sw=4:ts=4:et:
