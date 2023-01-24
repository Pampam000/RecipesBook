import sqlite3 as sq
from typing import NamedTuple

from app.create_logger import logger

tablename = 'recipes'

base = sq.connect('recipes_book.db')
base.execute(f"CREATE TABLE IF NOT EXISTS {tablename}("
             "name PRIMARY KEY, "
             "category, "
             "ingridients, "
             "description, "
             "photo_id)")
base.commit()
logger.info("Connected to db")
cursor = base.cursor()


class Recipe(NamedTuple):
    name: str
    category: str
    ingridients: str
    description: str
    photo_id: str


async def add_to_db(data: dict) -> str:
    try:
        cursor.execute(
            f"INSERT INTO {tablename} VALUES(?,?,?,?,?)", tuple(data.values()))
        base.commit()
        result_msg = 'Рецепт успешно добавлен'
        logger.info(f'{result_msg}: {Recipe(*data.values())}')
        return result_msg
    except Exception as e:
        result_msg = f'При добавлении рецепта произошла ошибка: {e}'
        logger.error(result_msg)
        return result_msg


async def get_all() -> list:
    db_result = cursor.execute(f"SELECT * FROM {tablename}").fetchall()
    result = [Recipe(*x) for x in db_result]
    logger.info(f'Получены все рецепты: {result}')
    return result


async def get_one_recipe(name: str) -> Recipe | None:
    name = name.capitalize()
    if db_result := cursor.execute(
            f"SELECT * from {tablename} WHERE name == ?", (name,)).fetchone():
        result = Recipe(*db_result)
        logger.info(f"Рецепт {result} найден в БД")
        return result
    else:
        logger.info(f"Рецепт '{name}' не найден в БД")
        return


async def get_all_in_category(category: str) -> list[Recipe]:
    db_result = cursor.execute(
        f"SELECT * FROM {tablename} WHERE category == ?", (category,))
    result = [Recipe(*x) for x in db_result]
    logger.info(f"Рецепты в категории '{category}': {result}")
    return result


async def delete_recipe(name: str) -> bool | None:
    if recipe := await get_one_recipe(name):
        cursor.execute(
            "DELETE FROM recipes WHERE name == ?", (recipe.name,)).fetchone()
        base.commit()

        logger.info(f'Рецепт удалён успешно: {Recipe(*recipe)}')
        return True


async def update(name: str, key: str, value: str):
    try:
        cursor.execute(
            f"UPDATE {tablename} SET {key} == ? WHERE name == ?",
            (value, name))
        base.commit()
        result_msg = "Рецепт успешно обновлён"
        logger.info(f'{result_msg}: у рeцепта "{name}" изменено поле "{key}".'
                    f' Новое значение: {value}')
        return result_msg
    except Exception as e:
        result_msg = f"Рецепт не обновлён\n Ошибка: {e}"
        logger.error(result_msg)
        return result_msg
