from aiosqlite import Cursor

from app.create_logger import logger
from app.keyboards.keyboard import cancel_keyboard
from .read import get_one_recipe
from .services import fsm_start, \
    create_inline_kb_categories
from ..connect import commit
from ..decorators import with_cursor
from ..schemas import DBRecipe, Answer

recipes = 'recipes'
categories = 'categories'


async def load_start(chat_id: int) -> Answer:
    return await fsm_start(chat_id, ('загрузку', 'загружать'))


async def check_recipe_name_in_db(name: str) -> Answer:
    db_result = await get_one_recipe(name)
    if not db_result.photo_id:
        return Answer(text="Укажите категорию",
                      reply_markup=await create_inline_kb_categories(),
                      go_next=True)
    else:
        return Answer(
            text=f"Рецепт c названием: '{name}' уже существует. Введите "
                 "другое название",
            reply_markup=cancel_keyboard)


@with_cursor
async def add_recipe(cursor: Cursor, data: dict):
    try:
        await cursor.execute(
            "INSERT INTO recipes VALUES(?,?,?,?,?)", tuple(data.values()))
        await commit()
        result_msg = f'Рецепт \'{data["name"]}\' успешно добавлен'
        logger.info(f'{result_msg}: {DBRecipe(*data.values())}')
        return result_msg
    except Exception as e:
        result_msg = 'При добавлении рецепта произошла ошибка'
        logger.error(result_msg + f": {e}")
        return result_msg
    # await cursor.execute("PRAGMA foreign_keys = ON;")
