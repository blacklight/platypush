import json

from threading import Event
from typing import List
from websocket import WebSocketApp

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.trello import MoveCardEvent, NewCardEvent, ArchivedCardEvent, \
        UnarchivedCardEvent

from platypush.plugins.trello import TrelloPlugin


class TrelloBackend(Backend):
    """
    This backend listens for events on a remote Trello account through websocket interface..
    Note that the Trello websocket interface
    `is not officially supported <https://community.developer.atlassian.com/t/websocket-interface/34586/4>`_
    and it requires a different token from the one you use for the Trello API (and for the Trello plugin).
    To get the websocket token:

        1. Open https://trello.com in your browser.
        2. Open the developer tools (F12), go to the Network tab, select 'Websocket' or 'WS' in the filter bar
           and refresh the page.
        3. You should see an entry in the format ``wss://trello.com/1/Session/socket?token=<token>``.
        4. Copy the ``<token>`` in the configuration of this backend.

    Requires:

        * The :class:`platypush.plugins.trello.TrelloPlugin` configured.

    Triggers:

        * :class:`platypush.message.event.trello.NewCardEvent` when a card is created.
        * :class:`platypush.message.event.MoveCardEvent` when a card is moved.
        * :class:`platypush.message.event.ArchivedCardEvent` when a card is archived/closed.
        * :class:`platypush.message.event.UnarchivedCardEvent` when a card is un-archived/opened.

    """

    _websocket_url_base = 'wss://trello.com/1/Session/socket?token={token}'

    def __init__(self, boards: List[str], token: str, **kwargs):
        """
        :param boards: List of boards to subscribe, by ID or name.
        :param token: Trello web client API token.
        """

        super().__init__(**kwargs)
        self._plugin: TrelloPlugin = get_plugin('trello')
        self.token = token
        self._req_id = 0
        self._boards_by_id = {}
        self._boards_by_name = {}

        for b in boards:
            b = self._plugin.get_board(b).board
            # noinspection PyUnresolvedReferences
            self._boards_by_id[b.id] = b
            # noinspection PyUnresolvedReferences
            self._boards_by_name[b.name] = b

        self.url = self._websocket_url_base.format(token=self.token)
        self._connected = Event()

        self._items = {}
        self._event_handled = False

    def _initialize_connection(self, ws: WebSocketApp):
        for board_id in self._boards_by_id.keys():
            self._send(ws, {
                'type': 'subscribe',
                'modelType': 'Board',
                'idModel': board_id,
                'tags': ['clientActions', 'updates'],
                'invitationTokens': [],
            })

        self.logger.info('Trello boards subscribed')

    def _on_msg(self):
        def hndl(*args):
            if len(args) < 2:
                self.logger.warning('Missing websocket argument - make sure that you are using '
                                    'a version of websocket-client < 0.53.0 or >= 0.58.0')
                return

            ws, msg = args[:2]
            if not msg:
                # Reply back with an empty message when the server sends an empty message
                ws.send('')
                return

            # noinspection PyBroadException
            try:
                msg = json.loads(msg)
            except Exception as e:
                self.logger.warning('Received invalid JSON message from Trello: {}: {}'.format(msg, e))
                return

            if 'error' in msg:
                self.logger.warning('Trello error: {}'.format(msg['error']))
                return

            if msg.get('reqid') == 0:
                self.logger.debug('Ping response received, subscribing boards')
                self._initialize_connection(ws)
                return

            notify = msg.get('notify')
            if not notify:
                return

            if notify['event'] != 'updateModels' or notify['typeName'] != 'Action':
                return

            for delta in notify['deltas']:
                args = {
                    'card_id': delta['data']['card']['id'],
                    'card_name': delta['data']['card']['name'],
                    'list_id': (delta['data'].get('list') or delta['data'].get('listAfter', {})).get('id'),
                    'list_name': (delta['data'].get('list') or delta['data'].get('listAfter', {})).get('name'),
                    'board_id': delta['data']['board']['id'],
                    'board_name': delta['data']['board']['name'],
                    'closed': delta.get('closed'),
                    'member_id': delta['memberCreator']['id'],
                    'member_username': delta['memberCreator']['username'],
                    'member_fullname': delta['memberCreator']['fullName'],
                    'date': delta['date'],
                }

                if delta.get('type') == 'createCard':
                    self.bus.post(NewCardEvent(**args))
                elif delta.get('type') == 'updateCard':
                    if 'listBefore' in delta['data']:
                        args.update({
                            'old_list_id': delta['data']['listBefore']['id'],
                            'old_list_name': delta['data']['listBefore']['name'],
                        })

                        self.bus.post(MoveCardEvent(**args))
                    elif 'closed' in delta['data'].get('old', {}):
                        cls = UnarchivedCardEvent if delta['data']['old']['closed'] else ArchivedCardEvent
                        self.bus.post(cls(**args))

        return hndl

    def _on_error(self):
        def hndl(*args):
            error = args[1] if len(args) > 1 else args[0]
            self.logger.warning('Trello websocket error: {}'.format(error))

        return hndl

    def _on_close(self):
        def hndl(*_):
            self.logger.warning('Trello websocket connection closed')
            self._connected.clear()
            self._req_id = 0

            while True:
                try:
                    self._connect()
                    self._connected.wait(timeout=20)
                    break
                except TimeoutError:
                    continue

        return hndl

    def _on_open(self):
        def hndl(*args):
            ws = args[0] if args else None
            self._connected.set()
            if ws:
                self._send(ws, {'type': 'ping'})
            self.logger.info('Trello websocket connected')

        return hndl

    def _send(self, ws: WebSocketApp, msg: dict):
        msg['reqid'] = self._req_id
        ws.send(json.dumps(msg))
        self._req_id += 1

    def _connect(self) -> WebSocketApp:
        return WebSocketApp(self.url,
                            on_open=self._on_open(),
                            on_message=self._on_msg(),
                            on_error=self._on_error(),
                            on_close=self._on_close())

    def run(self):
        super().run()
        self.logger.info('Started Todoist backend')
        ws = self._connect()
        ws.run_forever()


# vim:sw=4:ts=4:et:
