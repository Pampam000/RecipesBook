import aiosqlite as sq
from aiogram.types import ReplyKeyboardMarkup
from aiosqlite import Cursor

from app.create_logger import logger
from app.keyboards.keyboard import admin_keyboard, client_keyboard, \
    cancel_keyboard
from .schemas import DBRecipe, SendRecipe, Answer
from ..config import ADMINS_ID
from ..keyboards.inline_keyboard import inline_kb_category

recipes = 'recipes'
categories = 'categories'


async def connect_to_db():
    global connection
    connection = await sq.connect('recipes_book.db')
    logger.info("Connected to db")


async def disconnect():
    global connection
    await connection.close()
    logger.info("Disconnect db")


def with_cursor(func):
    async def wrapper(*args):
        async with connection.cursor() as cursor:
            return await func(cursor, *args)

    return wrapper


async def check_if_user_is_admin(chat_id: int) -> bool:
    return True if str(chat_id) in ADMINS_ID else False


async def get_user_keyboard(chat_id: int) -> ReplyKeyboardMarkup:
    return admin_keyboard if await check_if_user_is_admin(chat_id) else \
        client_keyboard


@with_cursor
async def get_all_recipes(cursor: Cursor) -> str:
    await cursor.execute(f"SELECT * FROM {recipes}")
    result = [DBRecipe(*x) for x in await cursor.fetchall()]
    logger.info(f'Получены все рецепты: {result}')

    return await _create_message_with_recipes_list(
        result, "Список рецептов пуст :(")


@with_cursor
async def get_all_recipes_in_category(cursor: Cursor, category: str) -> str:
    if await _check_category_in_db(category):

        await cursor.execute(
            f"SELECT * FROM {recipes} WHERE category == ?", (category,))
        result = [DBRecipe(*x) for x in await cursor.fetchall()]
        logger.info(f"Рецепты в категории '{category}': {result}")

        return await _create_message_with_recipes_list(
            result, f"Список рецептов в категории '{category}' пуст :(")
    else:
        return f"Категории '{category}' не существует. Попробуйте ещё раз"


@with_cursor
async def get_one_recipe(cursor: Cursor, name: str) -> SendRecipe:
    await cursor.execute(
        f"SELECT * from {recipes} WHERE name == ?", (name,))
    if db_result := await cursor.fetchone():

        recipe = DBRecipe(*db_result)
        logger.info(f"Рецепт {recipe} найден в БД")
        return SendRecipe(
            photo_id=recipe.photo_id,
            message=f"{recipe.name} ({recipe.category})\n\n "
                    f"{recipe.ingridients}\n\n {recipe.description}")

    else:
        msg = f"Рецепт '{name}' не найден"

        logger.info(msg)
        return SendRecipe(msg)


async def load_start(chat_id: int) -> Answer:
    return await _fsm_start(chat_id, ('загрузку', 'загружать'))


async def check_recipe_name_in_db(name: str) -> Answer:
    db_result = await get_one_recipe(name)
    if not db_result.photo_id:
        return Answer(text="Укажите категорию",
                      reply_markup=inline_kb_category,
                      go_next=True)
    else:
        return Answer(
            text=f"Рецепт c названием: '{name}' уже существует. Введите "
                 "другое название",
            reply_markup=cancel_keyboard)


@with_cursor
async def add_new_category_if_not_exists(cursor: Cursor, name: str):
    if not await _check_category_in_db(name):
        await cursor.execute(f"INSERT INTO {categories} VALUES(?)", (name,))
        await connection.commit()
        logger.info(f"Категория {name} добавлена в БД")


@with_cursor
async def add_recipe(cursor: Cursor, data: dict):
    try:
        await cursor.execute(
            "INSERT INTO recipes VALUES(?,?,?,?,?)", tuple(data.values()))
        await connection.commit()
        result_msg = f'Рецепт \'{data["name"]}\' успешно добавлен'
        logger.info(f'{result_msg}: {DBRecipe(*data.values())}')
        return result_msg
    except Exception as e:
        result_msg = 'При добавлении рецепта произошла ошибка'
        logger.error(result_msg + f": {e}")
        return result_msg
    # await cursor.execute("PRAGMA foreign_keys = ON;")


async def delete_start(chat_id: int) -> Answer:
    return await _fsm_start(chat_id, ('удаление', 'удалять'))


@with_cursor
async def delete_recipe_if_exists(cursor: Cursor, name: str):
    recipe = await get_one_recipe(name)
    if recipe.photo_id:
        await cursor.execute(
            "DELETE FROM recipes WHERE name == ?", (name,))
        await connection.commit()
        msg = f'Рецепт \'{name}\' удалён успешно'
        logger.info(msg)
        return Answer(msg, reply_markup=admin_keyboard, go_next=True)
    else:
        msg = f"Рецепт '{name}' не найден. Попробуйте ещё раз."
        logger.info(msg)
        return Answer(msg, reply_markup=cancel_keyboard)


async def update_start(chat_id: int) -> Answer:
    return await _fsm_start(chat_id, ('обновление', 'обновлять'))


@with_cursor
async def update(cursor: Cursor, name: str, key: str, value: str) -> str:
    try:

        await cursor.execute(
            f"UPDATE {recipes} SET {key} == ? WHERE name == ?",
            (value, name))
        await connection.commit()
        result_msg = "Рецепт успешно обновлён"
        logger.info(f'{result_msg}: у рeцепта "{name}" изменено поле "{key}".'
                    f' Новое значение: {value}')
        return result_msg
    except Exception as e:
        result_msg = f"Рецепт не обновлён"
        logger.error(result_msg + f"\n Ошибка: {e}")
        return result_msg


# @with_cursor
# async def get_all_categories(cursor: Cursor):
#
#     await cursor.execute(f"SELECT * FROM {categories}")
#     logger.info(await cursor.fetchall())


async def _create_message_with_recipes_list(recipes: list, msg: str) -> str:
    if recipes:

        result = ''
        for n, i in enumerate(recipes):
            result += f"{n + 1}. {i.name}\n"
        return result
    else:
        return msg


@with_cursor
async def _check_category_in_db(cursor: Cursor, category: str) -> bool:
    await cursor.execute(
        f"SELECT name FROM {categories} WHERE name == ?", (category,))
    if await cursor.fetchone():
        logger.info(f"Категория {category} найдена в БД")
        return True
    else:
        logger.info(f"Категория {category} НЕ найдена в БД")
        return False


async def _fsm_start(chat_id: int, actions: tuple[str]):
    if await check_if_user_is_admin(chat_id):
        logger.info(f'Пользователь {chat_id} является админом и начал '
                    f'{actions[0]} рецепта')
        return Answer(text="Введите название",
                      reply_markup=cancel_keyboard, go_next=True)
    else:
        logger.info(f'Пользователь {chat_id} НЕ является админом и хотел '
                    f'начать {actions[0]} рецепта')
        return Answer(f"Вы не можете {actions[1]} рецепты")
