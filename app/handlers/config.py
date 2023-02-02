from app.config import RECIPE_PARAMS_RU
from app.db.schemas import Answer
from app.handlers.states_groups import Update
from app.keyboards.inline_keyboard import inline_kb_category, inline_kb_update
from app.keyboards.keyboard import cancel_keyboard

_r1 = Answer(f"Введите новое название", reply_markup=cancel_keyboard,
             new_state=Update.change_name)

_r2 = Answer("На какую категорию заменить?", reply_markup=inline_kb_category,
             new_state=Update.change_category)

_r3 = Answer(f"Загрузите новое фото", reply_markup=cancel_keyboard,
             new_state=Update.change_photo)

_r4 = Answer(f"Введите новое значение", reply_markup=cancel_keyboard,
             new_state=Update.change_text)

CASES = {x: y for x, y in zip(RECIPE_PARAMS_RU, [_r1, _r2, _r3, _r4, _r4])}

WHAT_TO_CHANGE = Answer("Что будем менять?",
                        reply_markup=inline_kb_update)
