from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from .locales import VOTES_ACCEPT_GOPOST_BTNTEXT
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callbacks import SimpleCallbackData
from models.models import Poll, VoteOption, UserVoteItem
from config.settings import BOT_USERNAME


onVoteAcceptKeyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text=VOTES_ACCEPT_GOPOST_BTNTEXT
        )
    ]
], resize_keyboard=True)

onContactRequestKeyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text='Kontaktni yuborish',
            request_contact=True,
        )
    ]
])

def VotesInlineKeyboardBuilder(names_list: list):
    builder = InlineKeyboardBuilder()
    for name in names_list:
        # builder.button(text=name, callback_data=SimpleCallbackData(data='5'), switch_inline_query="",)
        builder.button(text=name, url='https://t.me/kwutzeebot?start=1&option=4')
    builder.adjust(1)
    return builder.as_markup()


def createInlineSchemaForPoll(poll : Poll):
    voteItemQuerySet = VoteOption.objects.filter(poll=poll)
    builder = InlineKeyboardBuilder()
    for voteOption in voteItemQuerySet:
        count = len(UserVoteItem.objects.filter(poll=poll, option=voteOption))
        builder.button(
            text=f"{voteOption.text} - {count}",
            url=f"https://t.me/{BOT_USERNAME}?start=poll_{poll.id}_vote_{voteOption.id}"
        )
    builder.adjust(1)
    return builder.as_markup()

