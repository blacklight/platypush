from dataclasses import dataclass
import datetime

from typing import Optional, List, Union


@dataclass
class TrelloList:
    """
    Represents a Trello list.
    """

    id: str
    name: str
    closed: bool
    subscribed: bool


@dataclass
class TrelloBoard:
    """
    Represents a Trello board.
    """

    id: str
    name: str
    url: str
    closed: bool
    lists: Optional[List[TrelloList]] = None
    description: Optional[str] = None
    date_last_activity: Optional[datetime.datetime] = None


@dataclass
class TrelloLabel:
    """
    Represents a Trello label.
    """

    id: str
    name: str
    color: Optional[str] = None


@dataclass
class TrelloUser:
    """
    Represents a Trello user.
    """

    id: str
    username: str
    fullname: str
    initials: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class TrelloComment:
    """
    Represents a Trello comment.
    """

    id: str
    text: str
    type: str
    creator: TrelloUser
    date: Union[str, datetime.datetime]


@dataclass
class TrelloPreview:
    """
    Represents a Trello preview.
    """

    id: str
    url: str
    scaled: bool
    size: int
    height: int
    width: int


@dataclass
class TrelloAttachment:
    """
    Represents a Trello attachment.
    """

    id: str
    size: int
    date: str
    edge_color: str
    member_id: str
    is_upload: bool
    name: str
    previews: List[TrelloPreview]
    url: str
    mime_type: Optional[str] = None


@dataclass
class TrelloChecklistItem:
    """
    Represents a Trello checklist item.
    """

    id: str
    name: str
    checked: bool


@dataclass
class TrelloChecklist:
    """
    Represents a Trello checklist.
    """

    id: str
    name: str
    items: List[TrelloChecklistItem]


@dataclass
class TrelloCard:
    """
    Represents a Trello card.
    """

    id: str
    name: str
    url: str
    closed: bool
    board: TrelloBoard
    is_due_complete: bool
    description: Optional[str] = None
    list: Optional[TrelloList] = None
    comments: Optional[List[TrelloComment]] = None
    labels: Optional[List[TrelloLabel]] = None
    attachments: Optional[List[TrelloAttachment]] = None
    checklists: Optional[List[TrelloChecklist]] = None
    due_date: Optional[Union[datetime.datetime, str]] = None
    latest_card_move_date: Optional[Union[datetime.datetime, str]] = None
    date_last_activity: Optional[Union[datetime.datetime, str]] = None


@dataclass
class TrelloMember:
    """
    Represents a Trello member.
    """

    id: str
    fullname: str
    bio: Optional[str]
    url: Optional[str]
    username: Optional[str]
    initials: Optional[str]
    member_type: Optional[str] = None


# vim:sw=4:ts=4:et:
