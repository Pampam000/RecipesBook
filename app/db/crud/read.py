from aiosqlite import Cursor

from app.create_logger import logger
from .services import check_category_in_db
from ..decorators import with_cursor
from ..schemas import DBRecipe

recipes = 'recipes'
categories = 'categories'


@with_cursor
async def get_all_recipes(cursor: Cursor) -> str:
    await cursor.execute(f"SELECT * FROM {recipes}")
    result = [DBRecipe(*x) for x in await cursor.fetchall()]
    logger.info(f'Получены все рецепты: {result}')

    return await _create_message_with_recipes_list(
        result, "Список рецептов пуст :(")


@with_cursor
async def get_all_recipes_in_category(cursor: Cursor, category: str) -> str:
    if await check_category_in_db(category):

        await cursor.execute(
            f"SELECT * FROM {recipes} WHERE category == ?", (category,))
        result = [DBRecipe(*x) for x in await cursor.fetchall()]
        logger.info(f"Рецепты в категории '{category}': {result}")

        return await _create_message_with_recipes_list(
            result, f"Список рецептов в категории '{category}' пуст :(")
    else:
        return f"Категории '{category}' не существует. Попробуйте ещё раз"


@with_cursor
async def get_one_recipe(cursor: Cursor, name: str) -> DBRecipe:
    await cursor.execute(
        f"SELECT * from {recipes} WHERE name == ?", (name,))
    if db_result := await cursor.fetchone():

        logger.info(f"Рецепт '{name}' найден в БД: {db_result}")
        return DBRecipe(*db_result)

    else:
        msg = f"Рецепт '{name}' не найден"
        logger.info(msg)
        return DBRecipe(msg)


async def _create_message_with_recipes_list(recipes: list, msg: str) -> str:
    if recipes:

        result = ''
        for n, i in enumerate(recipes):
            result += f"{n + 1}. {i.name}\n"
        return result
    else:
        return msg
