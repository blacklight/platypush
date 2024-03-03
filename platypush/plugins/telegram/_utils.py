import logging

from telegram import Message as TelegramMessage, User as TelegramUser

from platypush.schemas.telegram import (
    TelegramMessageSchema,
    TelegramUserSchema,
)

log = logging.getLogger(__name__)


def dump_msg(msg: TelegramMessage) -> dict:
    return dict(TelegramMessageSchema().dump(msg))


def dump_user(user: TelegramUser) -> dict:
    return dict(TelegramUserSchema().dump(user))


# vim:sw=4:ts=4:et:
