from typing import NamedTuple

from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup


class DBRecipe(NamedTuple):
    name: str
    category: str = None
    ingridients: str = None
    description: str = None
    photo_id: str = None

    async def as_tg_photo(self) -> dict:
        answer = {'photo': self._asdict()['photo_id'],
                  'caption': f"{self.name} ({self.category})\n\n "
                             f"{self.ingridients}\n\n {self.description}"}
        return answer

    async def as_tg_answ(self) -> dict:
        return {'text': self.name}


class Answer(NamedTuple):
    text: str
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup = None
    go_next: bool = False
    new_state: FSMContext = None

    async def as_tg_answer(self):
        tg_answer = self._asdict().copy()
        del tg_answer['go_next']
        del tg_answer['new_state']
        return tg_answer
