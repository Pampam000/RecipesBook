from app.config import RECIPE_PARAMS_RU
from app.db.crud import create_inline_kb_categories
from app.db.schemas import Answer
from app.handlers.states_groups import Update
from app.keyboards.inline_keyboard import inline_kb_update
from app.keyboards.keyboard import cancel_keyboard

_r1 = Answer(f"Введите новое название", reply_markup=cancel_keyboard,
             new_state=Update.change_name)

_r2 = Answer(f"Загрузите новое фото", reply_markup=cancel_keyboard,
             new_state=Update.change_photo)

_r3 = Answer(f"Введите новое значение", reply_markup=cancel_keyboard,
             new_state=Update.change_text)

_recipes_params_ru = RECIPE_PARAMS_RU.copy()
_recipes_params_ru.remove("Категория")

CASES = {x: y for x, y in zip(_recipes_params_ru, [_r1, _r2, _r3, _r3])}


async def create_cases():
    _r4 = Answer("На какую категорию заменить?",
                 reply_markup=await create_inline_kb_categories(),
                 new_state=Update.change_category)

    CASES["Категория"] = _r4
    return CASES


WHAT_TO_CHANGE = Answer("Что будем менять?",
                        reply_markup=inline_kb_update)
