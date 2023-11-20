import datetime
import json
from threading import Event
from typing import Optional, Dict, List, Union

import trello
from trello.board import Board, List as List_  # type: ignore
from trello.exceptions import ResourceUnavailable  # type: ignore
from websocket import WebSocketApp

from platypush.context import get_bus
from platypush.message.event.trello import (
    MoveCardEvent,
    NewCardEvent,
    ArchivedCardEvent,
    UnarchivedCardEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.trello import (
    TrelloBoardSchema,
    TrelloCardSchema,
    TrelloListSchema,
    TrelloMemberSchema,
)

from ._model import (
    TrelloBoard,
    TrelloCard,
    TrelloAttachment,
    TrelloPreview,
    TrelloChecklist,
    TrelloChecklistItem,
    TrelloUser,
    TrelloComment,
    TrelloLabel,
    TrelloList,
    TrelloMember,
)


class TrelloPlugin(RunnablePlugin):
    """
    Trello integration.

    You'll need a Trello API key. You can get it `here
    <https://trello.com/app-key>`_.

    You'll also need an auth token if you want to view/change private
    resources. You can generate a permanent token linked to your account on
    ``https://trello.com/1/connect?key=<KEY>&name=platypush&response_type=token&expiration=never&scope=read,write``.

    Also, polling of events requires you to follow a separate procedure to
    retrieve the Websocket tokens, since Trello uses a different (and
    undocumented) authorization mechanism:

        1. Open https://trello.com in your browser.
        2. Open the developer tools (F12).
        3. Go to the Cookies tab.
        4. Copy the value of the ``cloud.session.token`` cookie.

    """

    _websocket_url_base = 'wss://trello.com/1/Session/socket?clientVersion=build-194674'

    def __init__(
        self,
        api_key: str,
        api_secret: Optional[str] = None,
        token: Optional[str] = None,
        cloud_session_token: Optional[str] = None,
        boards: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        :param api_key: Trello API key. You can get it `here
            <https://trello.com/app-key>`_.
        :param api_secret: Trello API secret. You can get it `here
            <https://trello.com/app-key>`_.
        :param token: Trello token. It is required if you want to access or
            modify private resources. You can get a permanent token on
            ``https://trello.com/1/connect?key=<KEY>&name=platypush&response_type=token&expiration=never&scope=read,write``.
        :param cloud_session_token: Cloud session token. It is required
            if you want to monitor your boards for changes. See
            :class:`platypush.plugins.trello.TrelloPlugin` for the procedure to
            retrieve it.
        :param boards: List of boards to subscribe, by ID or name. If
            specified, then the plugin will listen for changes only on these boards.
        """

        super().__init__(**kwargs)
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = token
        self.cloud_session_token = cloud_session_token
        self._client = None
        self._req_id = 0
        self._boards_by_id = {}
        self._boards_by_name = {}
        self._monitored_boards = boards
        self.url = None

        if token:
            self.url = self._websocket_url_base

        self._connected = Event()
        self._items = {}
        self._event_handled = False
        self._ws: Optional[WebSocketApp] = None

    def _get_client(self) -> trello.TrelloClient:  # type: ignore
        if not self._client:
            self._client = trello.TrelloClient(  # type: ignore
                api_key=self.api_key,
                api_secret=self.api_secret,
                token=self.token,
            )

        return self._client

    def _get_board(self, board: str) -> Board:
        client = self._get_client()
        try:
            return client.get_board(board)
        except ResourceUnavailable:
            boards = [b for b in client.list_boards() if b.name == board]
            assert boards, f'No such board: {board}'
            return boards[0]

    def _get_boards(
        self, all: bool = False  # pylint: disable=redefined-builtin
    ) -> List[Board]:
        client = self._get_client()
        return client.list_boards(board_filter='all' if all else 'open')

    @action
    def get_boards(self, all: bool = False):  # pylint: disable=redefined-builtin
        """
        Get the list of boards.

        :param all: If True, return all the boards included those that have
            been closed/archived/deleted. Otherwise, only return open/active
            boards (default: False).
        :return: .. schema:: trello.TrelloBoardSchema(many=True)
        """
        return TrelloBoardSchema().dump(
            [
                TrelloBoard(
                    id=b.id,
                    name=b.name,
                    description=b.description,
                    url=b.url,
                    date_last_activity=b.date_last_activity,
                    closed=b.closed,
                )
                for b in self._get_boards(all=all)
            ],
            many=True,
        )

    @action
    def get_board(self, board: str):
        """
        Get the info about a board.

        :param board: Board ID or name
        :return: .. schema:: trello.TrelloBoardSchema
        """

        b = self._get_board(board)
        return TrelloBoardSchema().dump(
            TrelloBoard(
                id=b.id,
                name=b.name,
                url=b.url,
                closed=b.closed,
                description=b.description,
                date_last_activity=b.date_last_activity,
                lists=[
                    TrelloList(
                        id=ll.id,
                        name=ll.name,
                        closed=ll.closed,
                        subscribed=ll.subscribed,
                    )
                    for ll in b.list_lists()
                ],
            )
        )

    @action
    def open_board(self, board: str):
        """
        Re-open/un-archive a board.

        :param board: Board ID or name
        """
        self._get_board(board).open()

    @action
    def close_board(self, board: str):
        """
        Close/archive a board.

        :param board: Board ID or name
        """
        self._get_board(board).close()

    @action
    def set_board_name(self, board: str, name: str):
        """
        Change the name of a board.

        :param board: Board ID or name.
        :param name: New name.
        """
        self._get_board(board).set_name(name)
        return self.get_board(name)

    @action
    def set_board_description(self, board: str, description: str):
        """
        Change the description of a board.

        :param board: Board ID or name.
        :param description: New description.
        """
        self._get_board(board).set_description(description)
        return self.get_board(description)

    @action
    def create_label(self, board: str, name: str, color: Optional[str] = None):
        """
        Add a label to a board.

        :param board: Board ID or name
        :param name: Label name
        :param color: Optional HTML color
        """
        self._get_board(board).add_label(name=name, color=color)

    @action
    def delete_label(self, board: str, label: str):
        """
        Delete a label from a board.

        :param board: Board ID or name
        :param label: Label ID or name
        """

        b = self._get_board(board)

        try:
            b.delete_label(label)
        except ResourceUnavailable:
            label_ = next(iter(ll for ll in b.get_labels() if ll.name == label), None)
            assert label_, f'No such label: {label}'
            label = label_.id
            b.delete_label(label)

    @action
    def add_member(self, board: str, member_id: str, member_type: str = 'normal'):
        """
        Add a member to a board.

        :param board: Board ID or name.
        :param member_id: Member ID to add.
        :param member_type: Member type - can be 'normal' or 'admin' (default: 'normal').
        """
        self._get_board(board).add_member(member_id, member_type=member_type)

    @action
    def remove_member(self, board: str, member_id: str):
        """
        Remove a member from a board.

        :param board: Board ID or name.
        :param member_id: Member ID to remove.
        """
        self._get_board(board).remove_member(member_id)

    def _get_members(self, board: str, only_admin: bool = False):
        b = self._get_board(board)
        members = b.admin_members() if only_admin else b.get_members()

        return TrelloMemberSchema().dump(
            [
                TrelloMember(
                    id=m.id,
                    fullname=m.full_name,
                    bio=m.bio,
                    url=m.url,
                    username=m.username,
                    initials=m.initials,
                    member_type=getattr(m, 'member_type', None),
                )
                for m in members
            ],
            many=True,
        )

    @action
    def get_members(self, board: str):
        """
        Get the list of all the members of a board.

        :param board: Board ID or name.
        :return: .. schema:: trello.TrelloMemberSchema(many=True)
        """
        return self._get_members(board, only_admin=False)

    @action
    def get_admin_members(self, board: str):
        """
        Get the list of the admin members of a board.

        :param board: Board ID or name.
        :return: .. schema:: trello.TrelloMemberSchema(many=True)
        """
        return self._get_members(board, only_admin=True)

    @action
    def get_lists(
        self, board: str, all: bool = False  # pylint: disable=redefined-builtin
    ):
        """
        Get the list of lists on a board.

        :param board: Board ID or name
        :param all: If True, return all the lists, included those that have been closed/archived/deleted. Otherwise,
            only return open/active lists (default: False).
        :return: .. schema:: trello.TrelloListSchema(many=True)
        """
        return TrelloListSchema().dump(
            [
                TrelloList(
                    id=ll.id, name=ll.name, closed=ll.closed, subscribed=ll.subscribed
                )
                for ll in self._get_board(board).list_lists('all' if all else 'open')
            ],
            many=True,
        )

    @action
    def add_list(self, board: str, name: str, pos: Optional[int] = None):
        """
        Add a list to a board.

        :param board: Board ID or name
        :param name: List name
        :param pos: Optional position (default: last)
        """
        self._get_board(board).add_list(name=name, pos=pos)

    def _get_list(
        self, board: str, list: str  # pylint: disable=redefined-builtin
    ) -> List_:
        b = self._get_board(board)

        try:
            return b.get_list(list)
        except ResourceUnavailable:
            lists = [ll for ll in b.list_lists() if ll.name == list]
            assert lists, f'No such list: {list}'
            return lists[0]

    @action
    def set_list_name(
        self, board: str, list: str, name: str  # pylint: disable=redefined-builtin
    ):
        """
        Change the name of a board list.

        :param board: Board ID or name
        :param list: List ID or name
        :param name: New name
        """
        self._get_list(board, list).set_name(name)

    @action
    def list_subscribe(
        self, board: str, list: str  # pylint: disable=redefined-builtin
    ):
        """
        Subscribe to a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        self._get_list(board, list).subscribe()

    @action
    def list_unsubscribe(
        self, board: str, list: str  # pylint: disable=redefined-builtin
    ):
        """
        Unsubscribe from a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        self._get_list(board, list).unsubscribe()

    @action
    def archive_all_cards(
        self, board: str, list: str  # pylint: disable=redefined-builtin
    ):
        """
        Archive all the cards on a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        self._get_list(board, list).archive_all_cards()

    @action
    def move_all_cards(self, board: str, src: str, dest: str):
        """
        Move all the cards from a list to another.

        :param board: Board ID or name
        :param src: Source list
        :param dest: Target list
        """
        src_list = self._get_list(board, src)
        dest_list = self._get_list(board, dest)
        src_list.move_all_cards(dest_list.id)

    @action
    def open_list(self, board: str, list: str):  # pylint: disable=redefined-builtin
        """
        Open/un-archive a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        self._get_list(board, list).open()

    @action
    def close_list(self, board: str, list: str):  # pylint: disable=redefined-builtin
        """
        Close/archive a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        self._get_list(board, list).close()

    @action
    def move_list(
        self, board: str, list: str, position: int  # pylint: disable=redefined-builtin
    ):
        """
        Move a list to another position.

        :param board: Board ID or name
        :param list: List ID or name
        :param position: New position index
        """
        self._get_list(board, list).move(position)

    @action
    def add_card(
        self,
        board: str,
        list: str,  # pylint: disable=redefined-builtin
        name: str,
        description: Optional[str] = None,
        position: Optional[int] = None,
        labels: Optional[List[str]] = None,
        due: Optional[Union[str, datetime.datetime]] = None,
        source: Optional[str] = None,
        assign: Optional[List[str]] = None,
    ):
        """
        Add a card to a list.

        :param board: Board ID or name
        :param list: List ID or name
        :param name: Card name
        :param description: Card description
        :param position: Card position index
        :param labels: List of labels
        :param due: Due date (``datetime.datetime`` object or ISO-format string)
        :param source: Card ID to clone from
        :param assign: List of assignee member IDs
        :return: .. schema:: trello.TrelloCardSchema
        """
        list_ = self._get_list(board, list)

        if labels:
            labels = [
                ll
                for ll in list_.board.get_labels()
                if ll.id in labels or ll.name in labels
            ]

        card = list_.add_card(
            name=name,
            desc=description,
            labels=labels,
            due=due,
            source=source,
            position=position,
            assign=assign,
        )

        return TrelloCardSchema().dump(
            TrelloCard(
                id=card.id,
                name=card.name,
                url=card.url,
                closed=card.closed,
                board=TrelloBoard(
                    id=list_.board.id,
                    name=list_.board.name,
                    url=list_.board.url,
                    closed=list_.board.closed,
                    description=list_.board.description,
                    date_last_activity=list_.board.date_last_activity,
                ),
                is_due_complete=card.is_due_complete,
                list=None,
                comments=[],
                labels=[
                    TrelloLabel(id=lb.id, name=lb.name, color=lb.color)
                    for lb in (card.labels or [])
                ],
                description=card.description,
                due_date=card.due_date,
                latest_card_move_date=card.latestCardMove_date,
                date_last_activity=card.date_last_activity,
            )
        )

    @action
    def delete_card(self, card_id: str):
        """
        Permanently delete a card.

        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.delete()

    @action
    def open_card(self, card_id: str):
        """
        Open/un-archive a card.

        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.set_closed(False)

    @action
    def close_card(self, card_id: str):
        """
        Close/archive a card.

        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.set_closed(True)

    @action
    def add_checklist(
        self,
        card_id: str,
        title: str,
        items: List[str],
        states: Optional[List[bool]] = None,
    ):
        """
        Add a checklist to a card.

        :param card_id: Card ID
        :param title: Checklist title
        :param items: List of items in the checklist
        :param states: State of each item, True for checked, False for unchecked
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.add_checklist(title, items, states)

    @action
    def add_label(self, card_id: str, label: str):
        """
        Add a label to a card.

        :param card_id: Card ID
        :param label: Label name
        """
        client = self._get_client()
        card = client.get_card(card_id)

        labels = [ll for ll in card.board.get_labels() if ll.name == label]

        assert labels, f'No such label: {label}'
        label = labels[0]
        card.add_label(label)

    @action
    def remove_label(self, card_id: str, label: str):
        """
        Remove a label from a card.

        :param card_id: Card ID
        :param label: Label name
        """
        client = self._get_client()
        card = client.get_card(card_id)

        labels = [ll for ll in card.board.get_labels() if ll.name == label]

        assert labels, f'No such label: {label}'
        label = labels[0]
        card.remove_label(label)

    @action
    def assign_card(self, card_id: str, member_id: str):
        """
        Assign a card.

        :param card_id: Card ID
        :param member_id: Member ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.assign(member_id)

    @action
    def unassign_card(self, card_id: str, member_id: str):
        """
        Un-assign a card.

        :param card_id: Card ID
        :param member_id: Member ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.unassign(member_id)

    @action
    def attach_card(
        self,
        card_id: str,
        name: Optional[str] = None,
        mime_type: Optional[str] = None,
        file: Optional[str] = None,
        url: Optional[str] = None,
    ):
        """
        Add an attachment to a card. It can be either a local file or a remote URL.

        :param card_id: Card ID
        :param name: File name
        :param mime_type: MIME type
        :param file: Path to the file
        :param url: URL to the file
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.attach(name=name, mimeType=mime_type, file=file, url=url)

    @action
    def remove_attachment(self, card_id: str, attachment_id: str):
        """
        Remove an attachment from a card.

        :param card_id: Card ID
        :param attachment_id: Attachment ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.remove_attachment(attachment_id)

    @action
    def change_card_board(
        self,
        card_id: str,
        board: str,
        list: Optional[str] = None,  # pylint: disable=redefined-builtin
    ):
        """
        Move a card to a new board.

        :param card_id: Card ID
        :param board: New board ID or name
        :param list: Optional target list ID or name
        """
        client = self._get_client()
        card = client.get_card(card_id)
        board_id = self._get_board(board).id

        list_id = None
        if list:
            list_id = self._get_list(board_id, list).id

        card.change_board(board_id, list_id)

    @action
    def change_card_list(
        self, card_id: str, list: str  # pylint: disable=redefined-builtin
    ):
        """
        Move a card to a new list.

        :param card_id: Card ID
        :param list: List ID or name
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.change_list(self._get_list(card.board.id, list).id)

    @action
    def change_card_pos(self, card_id: str, position: int):
        """
        Move a card to a new position.

        :param card_id: Card ID
        :param position: New position index
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.change_pos(position)

    @action
    def comment_card(self, card_id: str, text: str):
        """
        Add a comment to a card.

        :param card_id: Card ID
        :param text: Comment text
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.comment(text)

    @action
    def update_comment(self, card_id: str, comment_id: str, text: str):
        """
        Update the content of a comment.

        :param card_id: Card ID
        :param comment_id: Comment ID
        :param text: New comment text
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.update_comment(comment_id, text)

    @action
    def delete_comment(self, card_id: str, comment_id: str):
        """
        Delete a comment.

        :param card_id: Card ID
        :param comment_id: Comment ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.delete_comment(comment_id)

    @action
    def set_card_name(self, card_id: str, name: str):
        """
        Change the name of a card.

        :param card_id: Card ID
        :param name: New name
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.set_name(name)

    @action
    def set_card_description(self, card_id: str, description: str):
        """
        Change the description of a card.

        :param card_id: Card ID
        :param description: New description
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.set_description(description)

    @action
    def add_card_member(self, card_id: str, member_id: str):
        """
        Add a member to a card.

        :param card_id: Card ID
        :param member_id: Member ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.add_member(member_id)

    @action
    def remove_card_member(self, card_id: str, member_id: str):
        """
        Remove a member from a card.

        :param card_id: Card ID
        :param member_id: Member ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.remove_member(member_id)

    @action
    def set_card_due(self, card_id: str, due: Union[str, datetime.datetime]):
        """
        Set the due date for a card.

        :param card_id: Card ID
        :param due: Due date, as a datetime.datetime object or an ISO string
        """
        client = self._get_client()
        card = client.get_card(card_id)

        if isinstance(due, str):
            due = datetime.datetime.fromisoformat(due)

        card.set_due(due)

    @action
    def remove_card_due(self, card_id: str):
        """
        Remove the due date from a card.

        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.remove_due()

    @action
    def set_card_due_complete(self, card_id: str):
        """
        Set the due date of a card as completed.

        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.set_due_complete()

    @action
    def remove_card_due_complete(self, card_id: str):
        """
        Remove the due complete flag from a card.

        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.remove_due_complete()

    @action
    def card_subscribe(self, card_id: str):
        """
        Subscribe to a card.
        :param card_id: Card ID
        """
        client = self._get_client()
        card = client.get_card(card_id)
        card.subscribe()

    @action
    def get_cards(
        self,
        board: str,
        list: Optional[str] = None,  # pylint: disable=redefined-builtin
        all: bool = False,  # pylint: disable=redefined-builtin
    ):
        """
        Get the list of cards on a board.

        :param board: Board ID or name
        :param list: List ID or name. If set then the method will only return the cards found on that list
            (default: None)
        :param all: If True, return all the cards included those that have been closed/archived/deleted. Otherwise,
            only return open/active cards (default: False).
        :return: .. schema:: trello.TrelloCardSchema(many=True)
        """

        b = self._get_board(board)
        lists: Dict[str, TrelloList] = {
            ll.id: TrelloList(
                id=ll.id, name=ll.name, closed=ll.closed, subscribed=ll.subscribed
            )
            for ll in b.list_lists()
        }

        list_id = None

        if list:
            if list in lists:
                list_id = list
            else:
                ll = next(
                    iter(
                        l1 for l1 in lists.values() if l1.name == list  # type: ignore
                    ),
                    None,
                )
                assert ll, f'No such list ID/name: {list}'
                list_id = ll.id  # type: ignore

        return TrelloCardSchema().dump(
            [
                TrelloCard(
                    id=c.id,
                    name=c.name,
                    url=c.url,
                    closed=c.closed,
                    list=lists.get(c.list_id),
                    board=TrelloBoard(
                        id=c.board.id,
                        name=c.board.name,
                        url=c.board.url,
                        closed=c.board.closed,
                        description=c.board.description,
                        date_last_activity=c.board.date_last_activity,
                    ),
                    attachments=[
                        TrelloAttachment(
                            id=a.get('id'),
                            url=a.get('url'),
                            size=a.get('bytes'),
                            date=a.get('date'),
                            edge_color=a.get('edgeColor'),
                            member_id=a.get('idMember'),
                            is_upload=a.get('isUpload'),
                            name=a.get('name'),
                            previews=[
                                TrelloPreview(
                                    id=p.get('id'),
                                    scaled=p.get('scaled'),
                                    url=p.get('url'),
                                    size=p.get('bytes'),
                                    height=p.get('height'),
                                    width=p.get('width'),
                                )
                                for p in a.get('previews', [])
                            ],
                            mime_type=a.get('mimeType'),
                        )
                        for a in c.attachments
                    ],
                    checklists=[
                        TrelloChecklist(
                            id=ch.id,
                            name=ch.name,
                            items=[
                                TrelloChecklistItem(
                                    id=i.get('id'),
                                    name=i.get('name'),
                                    checked=i.get('checked'),
                                )
                                for i in ch.items
                            ],
                        )
                        for ch in c.checklists
                    ],
                    comments=[
                        TrelloComment(
                            id=co.get('id'),
                            text=co.get('data', {}).get('text'),
                            type=co.get('type'),
                            date=co.get('date'),
                            creator=TrelloUser(
                                id=co.get('memberCreator', {}).get('id'),
                                username=co.get('memberCreator', {}).get('username'),
                                fullname=co.get('memberCreator', {}).get('fullName'),
                                initials=co.get('memberCreator', {}).get('initials'),
                                avatar_url=co.get('memberCreator', {}).get('avatarUrl'),
                            ),
                        )
                        for co in c.comments
                    ],
                    labels=[
                        TrelloLabel(id=lb.id, name=lb.name, color=lb.color)
                        for lb in (c.labels or [])
                    ],
                    is_due_complete=c.is_due_complete,
                    due_date=c.due_date,
                    description=c.description,
                    latest_card_move_date=c.latestCardMove_date,
                    date_last_activity=c.date_last_activity,
                )
                for c in b.all_cards()
                if ((all or not c.closed) and (not list or c.list_id == list_id))
            ],
            many=True,
        )

    def _initialize_connection(self, ws: WebSocketApp):
        boards = [
            b
            for b in (self._get_boards() or [])
            if not self._monitored_boards
            or b.id in self._monitored_boards
            or b.name in self._monitored_boards
        ]

        for b in boards:
            self._boards_by_id[b.id] = b
            self._boards_by_name[b.name] = b

        for board_id in self._boards_by_id.keys():
            self._send(
                ws,
                {
                    'type': 'subscribe',
                    'modelType': 'Board',
                    'idModel': board_id,
                    'tags': ['clientActions', 'updates'],
                    'invitationTokens': [],
                },
            )

        self.logger.info('Trello boards subscribed')

    def _on_msg(self, *args):  # pylint: disable=too-many-return-statements
        if len(args) < 2:
            self.logger.warning(
                'Missing websocket argument - make sure that you are using '
                'a version of websocket-client < 0.53.0 or >= 0.58.0'
            )
            return

        ws, msg = args[:2]
        if not msg:
            # Reply back with an empty message when the server sends an empty message
            ws.send('')
            return

        try:
            msg = json.loads(msg)
        except Exception as e:
            self.logger.warning(
                'Received invalid JSON message from Trello: %s: %s', msg, e
            )
            return

        if 'error' in msg:
            self.logger.warning('Trello error: %s', msg['error'])
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
                'list_id': (
                    delta['data'].get('list') or delta['data'].get('listAfter', {})
                ).get('id'),
                'list_name': (
                    delta['data'].get('list') or delta['data'].get('listAfter', {})
                ).get('name'),
                'board_id': delta['data']['board']['id'],
                'board_name': delta['data']['board']['name'],
                'closed': delta.get('closed'),
                'member_id': delta['memberCreator']['id'],
                'member_username': delta['memberCreator']['username'],
                'member_fullname': delta['memberCreator']['fullName'],
                'date': delta['date'],
            }

            if delta.get('type') == 'createCard':
                get_bus().post(NewCardEvent(**args))
            elif delta.get('type') == 'updateCard':
                if 'listBefore' in delta['data']:
                    args.update(
                        {
                            'old_list_id': delta['data']['listBefore']['id'],
                            'old_list_name': delta['data']['listBefore']['name'],
                        }
                    )

                    get_bus().post(MoveCardEvent(**args))
                elif 'closed' in delta['data'].get('old', {}):
                    cls = (
                        UnarchivedCardEvent
                        if delta['data']['old']['closed']
                        else ArchivedCardEvent
                    )
                    get_bus().post(cls(**args))

    def _on_error(self, *args):
        error = args[1] if len(args) > 1 else args[0]
        self.logger.warning('Trello websocket error: %s', error)

    def _on_close(self, *_):
        self.logger.warning('Trello websocket connection closed')
        self._connected.clear()
        self._req_id = 0

        while not self.should_stop():
            try:
                self._connect(reconnect=True)
                self._connected.wait(timeout=10)
                break
            except TimeoutError:
                continue

    def _on_open(self, *args):
        ws = args[0] if args else None
        self._connected.set()
        if ws:
            self._send(ws, {'type': 'ping'})
        self.logger.info('Trello websocket connected')

    def _send(self, ws: WebSocketApp, msg: dict):
        msg['reqid'] = self._req_id
        ws.send(json.dumps(msg))
        self._req_id += 1

    def _connect(self, reconnect: bool = False) -> WebSocketApp:
        assert self.url, 'Trello websocket URL not set'
        if reconnect:
            self.stop()

        if not self._ws:
            self._ws = WebSocketApp(
                self.url,
                header={
                    'Cookie': (
                        f'token={self.token}; '
                        f'cloud.session.token={self.cloud_session_token}'
                    )
                },
                on_open=self._on_open,
                on_message=self._on_msg,
                on_error=self._on_error,
                on_close=self._on_close,
            )

        return self._ws

    def main(self):
        if not self.url:
            self.logger.info(
                "token/cloud_session_token not set: your Trello boards won't be monitored for changes"
            )
            self.wait_stop()
        else:
            ws = self._connect()
            ws.run_forever()

    def stop(self):
        if self._ws:
            self._ws.close()
            self._ws = None


# vim:sw=4:ts=4:et:
