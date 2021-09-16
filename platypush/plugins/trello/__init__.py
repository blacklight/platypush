import datetime

from typing import Optional, Dict, List, Union

# noinspection PyPackageRequirements
import trello
# noinspection PyPackageRequirements
from trello.board import Board, List as List_
# noinspection PyPackageRequirements
from trello.exceptions import ResourceUnavailable

from platypush.message.response.trello import TrelloBoard, TrelloBoardsResponse, TrelloCardsResponse, TrelloCard, \
    TrelloAttachment, TrelloPreview, TrelloChecklist, TrelloChecklistItem, TrelloUser, TrelloComment, TrelloLabel, \
    TrelloList, TrelloBoardResponse, TrelloListsResponse, TrelloMembersResponse, TrelloMember, TrelloCardResponse

from platypush.plugins import Plugin, action


class TrelloPlugin(Plugin):
    """
    Trello integration.

    Requires:

        * **py-trello** (``pip install py-trello``)

    You'll also need a Trello API key. You can get it `here <https://trello.com/app-key>`.
    You'll also need an auth token if you want to view/change private resources. You can generate a permanent token
    linked to your account on
    https://trello.com/1/connect?key=<KEY>&name=platypush&response_type=token&expiration=never&scope=read,write
    """

    def __init__(self, api_key: str, api_secret: Optional[str] = None, token: Optional[str] = None, **kwargs):
        """
        :param api_key: Trello API key. You can get it `here <https://trello.com/app-key>`.
        :param api_secret: Trello API secret. You can get it `here <https://trello.com/app-key>`.
        :param token: Trello token. It is required if you want to access or modify private resources. You can get
            a permanent token on
            https://trello.com/1/connect?key=<KEY>&name=platypush&response_type=token&expiration=never&scope=read,write
        """

        super().__init__(**kwargs)
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = token
        self._client = None

    def _get_client(self) -> trello.TrelloClient:
        if not self._client:
            self._client = trello.TrelloClient(
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
            assert boards, 'No such board: {}'.format(board)
            return boards[0]

    # noinspection PyShadowingBuiltins
    @action
    def get_boards(self, all: bool = False) -> TrelloBoardsResponse:
        """
        Get the list of boards.

        :param all: If True, return all the boards included those that have been closed/archived/deleted. Otherwise,
            only return open/active boards (default: False).
        """
        client = self._get_client()

        return TrelloBoardsResponse([
            TrelloBoard(
                id=b.id,
                name=b.name,
                description=b.description,
                url=b.url,
                date_last_activity=b.date_last_activity,
                closed=b.closed,
            )
            for b in client.list_boards(board_filter='all' if all else 'open')
        ])

    @action
    def get_board(self, board: str) -> TrelloBoardResponse:
        """
        Get the info about a board.

        :param board: Board ID or name
        """

        board = self._get_board(board)
        return TrelloBoardResponse(
            TrelloBoard(
                id=board.id,
                name=board.name,
                url=board.url,
                closed=board.closed,
                description=board.description,
                date_last_activity=board.date_last_activity,
                lists=[
                    TrelloList(id=ll.id, name=ll.name, closed=ll.closed, subscribed=ll.subscribed)
                    for ll in board.list_lists()
                ]
            )
        )

    @action
    def open_board(self, board: str):
        """
        Re-open/un-archive a board.

        :param board: Board ID or name
        """
        board = self._get_board(board)
        board.open()

    @action
    def close_board(self, board: str):
        """
        Close/archive a board.

        :param board: Board ID or name
        """
        board = self._get_board(board)
        board.close()

    @action
    def set_board_name(self, board: str, name: str):
        """
        Change the name of a board.

        :param board: Board ID or name.
        :param name: New name.
        """
        board = self._get_board(board)
        board.set_name(name)
        return self.get_board(name)

    @action
    def set_board_description(self, board: str, description: str):
        """
        Change the description of a board.

        :param board: Board ID or name.
        :param description: New description.
        """
        board = self._get_board(board)
        board.set_description(description)
        return self.get_board(description)

    @action
    def create_label(self, board: str, name: str, color: Optional[str] = None):
        """
        Add a label to a board.

        :param board: Board ID or name
        :param name: Label name
        :param color: Optional HTML color
        """
        board = self._get_board(board)
        board.add_label(name=name, color=color)

    @action
    def delete_label(self, board: str, label: str):
        """
        Delete a label from a board.

        :param board: Board ID or name
        :param label: Label ID or name
        """

        board = self._get_board(board)

        try:
            board.delete_label(label)
        except ResourceUnavailable:
            labels = [
                ll for ll in board.get_labels()
                if ll.name == label
            ]

            assert labels, 'No such label: {}'.format(label)
            label = labels[0].id
            board.delete_label(label)

    @action
    def add_member(self, board: str, member_id: str, member_type: str = 'normal'):
        """
        Add a member to a board.

        :param board: Board ID or name.
        :param member_id: Member ID to add.
        :param member_type: Member type - can be 'normal' or 'admin' (default: 'normal').
        """
        board = self._get_board(board)
        board.add_member(member_id, member_type=member_type)

    @action
    def remove_member(self, board: str, member_id: str):
        """
        Remove a member from a board.

        :param board: Board ID or name.
        :param member_id: Member ID to remove.
        """
        board = self._get_board(board)
        board.remove_member(member_id)

    def _get_members(self, board: str, only_admin: bool = False) -> TrelloMembersResponse:
        board = self._get_board(board)
        members = board.admin_members() if only_admin else board.get_members()

        return TrelloMembersResponse([
            TrelloMember(
                id=m.id,
                full_name=m.full_name,
                bio=m.bio,
                url=m.url,
                username=m.username,
                initials=m.initials,
                member_type=getattr(m, 'member_type') if hasattr(m, 'member_type') else None
            )
            for m in members
        ])

    @action
    def get_members(self, board: str) -> TrelloMembersResponse:
        """
        Get the list of all the members of a board.
        :param board: Board ID or name.
        """
        return self._get_members(board, only_admin=False)

    @action
    def get_admin_members(self, board: str) -> TrelloMembersResponse:
        """
        Get the list of the admin members of a board.
        :param board: Board ID or name.
        """
        return self._get_members(board, only_admin=True)

    # noinspection PyShadowingBuiltins
    @action
    def get_lists(self, board: str, all: bool = False) -> TrelloListsResponse:
        """
        Get the list of lists on a board.

        :param board: Board ID or name
        :param all: If True, return all the lists, included those that have been closed/archived/deleted. Otherwise,
            only return open/active lists (default: False).
        """

        board = self._get_board(board)
        return TrelloListsResponse([
            TrelloList(id=ll.id, name=ll.name, closed=ll.closed, subscribed=ll.subscribed)
            for ll in board.list_lists('all' if all else 'open')
        ])

    @action
    def add_list(self, board: str, name: str, pos: Optional[int] = None):
        """
        Add a list to a board.

        :param board: Board ID or name
        :param name: List name
        :param pos: Optional position (default: last)
        """

        board = self._get_board(board)
        board.add_list(name=name, pos=pos)

    # noinspection PyShadowingBuiltins
    def _get_list(self, board: str, list: str) -> List_:
        board = self._get_board(board)

        try:
            return board.get_list(list)
        except ResourceUnavailable:
            lists = [ll for ll in board.list_lists() if ll.name == list]
            assert lists, 'No such list: {}'.format(list)
            return lists[0]

    # noinspection PyShadowingBuiltins
    @action
    def set_list_name(self, board: str, list: str, name: str):
        """
        Change the name of a board list.

        :param board: Board ID or name
        :param list: List ID or name
        :param name: New name
        """
        list = self._get_list(board, list)
        list.set_name(name)

    # noinspection PyShadowingBuiltins
    @action
    def list_subscribe(self, board: str, list: str):
        """
        Subscribe to a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        list = self._get_list(board, list)
        list.subscribe()

    # noinspection PyShadowingBuiltins
    @action
    def list_unsubscribe(self, board: str, list: str):
        """
        Unsubscribe from a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        list = self._get_list(board, list)
        list.unsubscribe()

    # noinspection PyShadowingBuiltins
    @action
    def archive_all_cards(self, board: str, list: str):
        """
        Archive all the cards on a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        list = self._get_list(board, list)
        list.archive_all_cards()

    @action
    def move_all_cards(self, board: str, src: str, dest: str):
        """
        Move all the cards from a list to another.

        :param board: Board ID or name
        :param src: Source list
        :param dest: Target list
        """
        src = self._get_list(board, src)
        dest = self._get_list(board, dest)
        src.move_all_cards(dest.id)

    # noinspection PyShadowingBuiltins
    @action
    def open_list(self, board: str, list: str):
        """
        Open/un-archive a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        list = self._get_list(board, list)
        list.open()

    # noinspection PyShadowingBuiltins
    @action
    def close_list(self, board: str, list: str):
        """
        Close/archive a list.

        :param board: Board ID or name
        :param list: List ID or name
        """
        list = self._get_list(board, list)
        list.close()

    # noinspection PyShadowingBuiltins
    @action
    def move_list(self, board: str, list: str, position: int):
        """
        Move a list to another position.

        :param board: Board ID or name
        :param list: List ID or name
        :param position: New position index
        """
        list = self._get_list(board, list)
        list.move(position)

    # noinspection PyShadowingBuiltins
    @action
    def add_card(self, board: str, list: str, name: str, description: Optional[str] = None,
                 position: Optional[int] = None, labels: Optional[List[str]] = None,
                 due: Optional[Union[str, datetime.datetime]] = None, source: Optional[str] = None,
                 assign: Optional[List[str]] = None) -> TrelloCardResponse:
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
        """
        list = self._get_list(board, list)

        if labels:
            labels = [
                ll for ll in list.board.get_labels()
                if ll.id in labels or ll.name in labels
            ]

        card = list.add_card(name=name, desc=description, labels=labels, due=due, source=source, position=position,
                             assign=assign)

        return TrelloCardResponse(TrelloCard(id=card.id,
                                             name=card.name,
                                             url=card.url,
                                             closed=card.closed,
                                             board=TrelloBoard(
                                                 id=list.board.id,
                                                 name=list.board.name,
                                                 url=list.board.url,
                                                 closed=list.board.closed,
                                                 description=list.board.description,
                                                 date_last_activity=list.board.date_last_activity
                                             ),

                                             is_due_complete=card.is_due_complete,
                                             list=None,
                                             comments=[],
                                             labels=[
                                                 TrelloLabel(
                                                     id=lb.id,
                                                     name=lb.name,
                                                     color=lb.color
                                                 )
                                                 for lb in (card.labels or [])
                                             ],
                                             description=card.description,
                                             due_date=card.due_date,
                                             latest_card_move_date=card.latestCardMove_date,
                                             date_last_activity=card.date_last_activity
                                             ))

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
    def add_checklist(self, card_id: str, title: str, items: List[str], states: Optional[List[bool]] = None):
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

        labels = [
            ll for ll in card.board.get_labels()
            if ll.name == label
        ]

        assert labels, 'No such label: {}'.format(label)
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

        labels = [
            ll for ll in card.board.get_labels()
            if ll.name == label
        ]

        assert labels, 'No such label: {}'.format(label)
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
    def attach_card(self, card_id: str, name: Optional[str] = None, mime_type: Optional[str] = None,
                    file: Optional[str] = None, url: Optional[str] = None):
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

    # noinspection PyShadowingBuiltins
    @action
    def change_card_board(self, card_id: str, board: str, list: str = None):
        """
        Move a card to a new board.

        :param card_id: Card ID
        :param board: New board ID or name
        :param list: Optional target list ID or name
        """
        client = self._get_client()
        card = client.get_card(card_id)
        board = self._get_board(board)

        list_id = None
        if list:
            list_id = self._get_list(board.id, list).id

        card.change_board(board.id, list_id)

    # noinspection PyShadowingBuiltins
    @action
    def change_card_list(self, card_id: str, list: str):
        """
        Move a card to a new list.

        :param card_id: Card ID
        :param list: List ID or name
        """
        client = self._get_client()
        card = client.get_card(card_id)
        list = self._get_list(card.board.id, list)
        card.change_list(list.id)

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

    # noinspection PyShadowingBuiltins
    @action
    def get_cards(self, board: str, list: Optional[str] = None, all: bool = False) -> TrelloCardsResponse:
        """
        Get the list of cards on a board.

        :param board: Board ID or name
        :param list: List ID or name. If set then the method will only return the cards found on that list
            (default: None)
        :param all: If True, return all the cards included those that have been closed/archived/deleted. Otherwise,
            only return open/active cards (default: False).
        """

        board = self._get_board(board)
        lists: Dict[str, TrelloList] = {
            ll.id: TrelloList(id=ll.id, name=ll.name, closed=ll.closed, subscribed=ll.subscribed)
            for ll in board.list_lists()
        }

        list_id = None

        if list:
            if list in lists:
                list_id = list
            else:
                # noinspection PyUnresolvedReferences
                ll = [l1 for l1 in lists.values() if l1.name == list]
                assert ll, 'No such list ID/name: {}'.format(list)
                # noinspection PyUnresolvedReferences
                list_id = ll[0].id

        # noinspection PyUnresolvedReferences
        return TrelloCardsResponse([
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
                    date_last_activity=c.board.date_last_activity
                ),

                attachments=[
                    TrelloAttachment(
                        id=a.get('id'),
                        bytes=a.get('bytes'),
                        date=a.get('date'),
                        edge_color=a.get('edgeColor'),
                        id_member=a.get('idMember'),
                        is_upload=a.get('isUpload'),
                        name=a.get('name'),
                        previews=[
                            TrelloPreview(
                                id=p.get('id'),
                                scaled=p.get('scaled'),
                                url=p.get('url'),
                                bytes=p.get('bytes'),
                                height=p.get('height'),
                                width=p.get('width')
                            )
                            for p in a.get('previews', [])
                        ],
                        url=a.get('url'),
                        mime_type=a.get('mimeType')
                    )
                    for a in c.attachments
                ],

                checklists=[
                    TrelloChecklist(
                        id=ch.id,
                        name=ch.name,
                        checklist_items=[
                            TrelloChecklistItem(
                                id=i.get('id'),
                                name=i.get('name'),
                                checked=i.get('checked')
                            )
                            for i in ch.items
                        ]
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
                            avatar_url=co.get('memberCreator', {}).get('avatarUrl')
                        )
                    )
                    for co in c.comments
                ],

                labels=[
                    TrelloLabel(
                        id=lb.id,
                        name=lb.name,
                        color=lb.color
                    )
                    for lb in (c.labels or [])
                ],

                is_due_complete=c.is_due_complete,
                due_date=c.due_date,
                description=c.description,
                latest_card_move_date=c.latestCardMove_date,
                date_last_activity=c.date_last_activity
            )
            for c in board.all_cards() if (
                (all or not c.closed) and
                (not list or c.list_id == list_id)
            )
        ])


# vim:sw=4:ts=4:et:
