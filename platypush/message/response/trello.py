import datetime

from typing import Optional, List, Union

from platypush.message import Mapping
from platypush.message.response import Response


class TrelloResponse(Response):
    pass


class TrelloList(Mapping):
    def __init__(self,
                 id: str,
                 name: str,
                 closed: bool,
                 subscribed: bool,
                 *args, **kwargs):
        super().__init__(id=id, name=name, closed=closed, subscribed=subscribed, *args, **kwargs)


class TrelloBoard(Mapping):
    def __init__(self,
                 id: str,
                 name: str,
                 url: str,
                 closed: bool,
                 lists: Optional[List[TrelloList]] = None,
                 description: Optional[str] = None,
                 date_last_activity: Optional[datetime.datetime] = None,
                 *args, **kwargs):
        super().__init__(id=id, name=name, url=url, closed=closed, description=description, lists=lists,
                         date_last_activity=date_last_activity, *args, **kwargs)


class TrelloBoardResponse(TrelloResponse):
    def __init__(self, board: TrelloBoard, **kwargs):
        super().__init__(output=board, **kwargs)
        self.board = board


class TrelloBoardsResponse(TrelloResponse):
    def __init__(self, boards: List[TrelloBoard], **kwargs):
        super().__init__(output=boards, **kwargs)


class TrelloListsResponse(TrelloResponse):
    def __init__(self, lists: List[TrelloList], **kwargs):
        super().__init__(output=lists, **kwargs)


class TrelloLabel(Mapping):
    def __init__(self,
                 id: str,
                 name: str,
                 color: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(id=id, name=name, color=color, *args, **kwargs)


class TrelloUser(Mapping):
    def __init__(self,
                 id: str,
                 username: str,
                 fullname: str,
                 initials: Optional[str] = None,
                 avatar_url: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(id=id, username=username, fullname=fullname, initials=initials,
                         avatar_url=avatar_url, *args, **kwargs)


class TrelloComment(Mapping):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 id: str,
                 text: str,
                 type: str,
                 creator: TrelloUser,
                 date: Union[str, datetime.datetime],
                 *args, **kwargs):
        super().__init__(id=id, text=text, type=type, creator=creator, date=date, *args, **kwargs)


class TrelloCard(Mapping):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 id: str,
                 name: str,
                 url: str,
                 closed: bool,
                 board: TrelloBoard,
                 is_due_complete: bool,
                 list: Optional[TrelloList] = None,
                 comments: Optional[List[TrelloComment]] = None,
                 labels: Optional[List[TrelloLabel]] = None,
                 description: Optional[str] = None,
                 due_date: Optional[Union[datetime.datetime, str]] = None,
                 latest_card_move_date: Optional[Union[datetime.datetime, str]] = None,
                 date_last_activity: Optional[Union[datetime.datetime, str]] = None,
                 *args, **kwargs):
        super().__init__(id=id, name=name, url=url, closed=closed, board=board, is_due_complete=is_due_complete,
                         description=description, date_last_activity=date_last_activity, due_date=due_date, list=list,
                         comments=comments, labels=labels, latest_card_move_date=latest_card_move_date, *args, **kwargs)


class TrelloCardResponse(TrelloResponse):
    def __init__(self, card: TrelloCard, **kwargs):
        super().__init__(output=card, **kwargs)


class TrelloCardsResponse(TrelloResponse):
    def __init__(self, cards: List[TrelloCard], **kwargs):
        super().__init__(output=cards, **kwargs)


class TrelloPreview(Mapping):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 id: str,
                 scaled: bool,
                 url: str,
                 bytes: int,
                 height: int,
                 width: int,
                 *args, **kwargs):
        super().__init__(id=id, scaled=scaled, url=url, bytes=bytes, height=height, width=width, *args, **kwargs)


class TrelloAttachment(Mapping):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 id: str,
                 bytes: int,
                 date: str,
                 edge_color: str,
                 id_member: str,
                 is_upload: bool,
                 name: str,
                 previews: List[TrelloPreview],
                 url: str,
                 mime_type: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(id=id, bytes=bytes, date=date, edge_color=edge_color, id_member=id_member, is_upload=is_upload,
                         name=name, previews=previews, url=url, mime_type=mime_type, *args, **kwargs)


class TrelloChecklistItem(Mapping):
    def __init__(self,
                 id: str,
                 name: str,
                 checked: bool,
                 *args, **kwargs):
        super().__init__(id=id, name=name, checked=checked, *args, **kwargs)


class TrelloChecklist(Mapping):
    def __init__(self,
                 id: str,
                 name: str,
                 checklist_items: List[TrelloChecklistItem],
                 *args, **kwargs):
        super().__init__(id=id, name=name, checklist_items=checklist_items, *args, **kwargs)


class TrelloMember(Mapping):
    def __init__(self,
                 id: str,
                 full_name: str,
                 bio: Optional[str],
                 url: Optional[str],
                 username: Optional[str],
                 initials: Optional[str],
                 member_type: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(id=id, full_name=full_name, bio=bio, url=url, username=username, initials=initials,
                         member_type=member_type, *args, **kwargs)


class TrelloMembersResponse(Mapping):
    def __init__(self, members: List[TrelloMember], **kwargs):
        super().__init__(output=members, **kwargs)


# vim:sw=4:ts=4:et:
