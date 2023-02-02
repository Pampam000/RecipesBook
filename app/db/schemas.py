from typing import NamedTuple

from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup


class DBRecipe(NamedTuple):
    name: str
    category: str
    ingridients: str
    description: str
    photo_id: str


class SendRecipe(NamedTuple):
    message: str
    photo_id: str = None


class Answer(NamedTuple):
    text: str
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup = None
    go_next: bool = False
    new_state: FSMContext = None

    def as_tg_answer(self):
        tg_answer = self._asdict().copy()
        del tg_answer['go_next']
        del tg_answer['new_state']
        return tg_answer
