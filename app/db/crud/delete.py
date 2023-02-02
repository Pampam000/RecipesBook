from aiosqlite import Cursor

from app.create_logger import logger
from app.keyboards.keyboard import admin_keyboard, cancel_keyboard
from .read import get_one_recipe
from .services import fsm_start
from ..connect import commit
from ..decorators import with_cursor
from ..schemas import Answer

recipes = 'recipes'
categories = 'categories'


async def delete_start(chat_id: int) -> Answer:
    return await fsm_start(chat_id, ('удаление', 'удалять'))


@with_cursor
async def delete_recipe_if_exists(cursor: Cursor, name: str):
    recipe = await get_one_recipe(name)
    if recipe.photo_id:
        await cursor.execute(
            "DELETE FROM recipes WHERE name == ?", (name,))
        await commit()
        msg = f'Рецепт \'{name}\' удалён успешно'
        logger.info(msg)
        return Answer(msg, reply_markup=admin_keyboard, go_next=True)
    else:
        msg = f"Рецепт '{name}' не найден. Попробуйте ещё раз."
        logger.info(msg)
        return Answer(msg, reply_markup=cancel_keyboard)
