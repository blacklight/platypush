import datetime

from platypush.message.event import Event


class TrelloEvent(Event):
    pass


class CardEvent(TrelloEvent):
    def __init__(self,
                 card_id: str,
                 card_name: str,
                 list_id: str,
                 list_name: str,
                 board_id: str,
                 board_name: str,
                 closed: bool,
                 member_id: str,
                 member_username: str,
                 member_fullname: str,
                 date: datetime.datetime,
                 *args, **kwargs):
        super().__init__(*args,
                         card_id=card_id,
                         card_name=card_name,
                         list_id=list_id,
                         list_name=list_name,
                         board_id=board_id,
                         board_name=board_name,
                         closed=closed,
                         member_id=member_id,
                         member_username=member_username,
                         member_fullname=member_fullname,
                         date=date,
                         **kwargs)


class NewCardEvent(CardEvent):
    """
    Event triggered when a card is created.
    """


class MoveCardEvent(CardEvent):
    """
    Event triggered when a card is moved to another list.
    """

    def __init__(self, old_list_id: str, old_list_name: str, *args, **kwargs):
        super().__init__(*args, old_list_id=old_list_id, old_list_name=old_list_name, **kwargs)


class ArchivedCardEvent(CardEvent):
    """
    Event triggered when a card is archived.
    """

    def __init__(self, *args, **kwargs):
        kwargs['old_closed'] = False
        super().__init__(*args, **kwargs)



class UnarchivedCardEvent(CardEvent):
    """
    Event triggered when a card is un-archived.
    """

    def __init__(self, *args, **kwargs):
        kwargs['old_closed'] = True
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:
