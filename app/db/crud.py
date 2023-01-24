import sqlite3 as sq
from typing import NamedTuple

tablename = 'recipes'
base = sq.connect('recipes_book.db')
base.execute(f"CREATE TABLE IF NOT EXISTS {tablename}("
             "name PRIMARY KEY, "
             "category, "
             "ingridients, "
             "description, "
             "photo_id)")
base.commit()
print("Connected to db")
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
        return 'Рецепт успешно добавлен'
    except Exception as e:
        return f'Произошла ошибка {e} при добавлении рецепта'


async def get_all() -> list:
    db_result = cursor.execute(f"SELECT * FROM {tablename}").fetchall()
    return [Recipe(*x) for x in db_result]


async def get_one_recipe(name: str) -> Recipe | None:
    name = name.capitalize()
    if db_result := cursor.execute(
            f"SELECT * from {tablename} WHERE name == ?", (name,)).fetchone():
        return Recipe(*db_result)


async def get_all_in_category(category: str) -> list[Recipe]:
    db_result = cursor.execute(
        f"SELECT * FROM {tablename} WHERE category == ?", (category,))
    return [Recipe(*x) for x in db_result]


async def delete_recipe(name: str) -> bool | None:
    if recipe := await get_one_recipe(name):
        cursor.execute(
            "DELETE FROM recipes WHERE name == ?", (recipe.name,)).fetchone()
        base.commit()
        return True


async def update(name: str, key: str, value: str):
    try:
        cursor.execute(
            f"UPDATE {tablename} SET {key} == ? WHERE name == ?", (value, name))
        base.commit()
        return "Рецепт успешно обновлён"
    except Exception as e:
        return f"Рецепт не обновлён\n Ошибка: {e}"
