import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS_ID = os.getenv("ADMINS_ID")

RECIPE_PARAMS_RU = ('Название', 'Категория', 'Фото', 'Ингридиенты', 'Описание')
RECIPE_PARAMS_EN = ('name', 'category', 'photo_id', 'ingridients',
                    'description')
RECIPE_PARAMS = {x: y for x, y in zip(RECIPE_PARAMS_RU, RECIPE_PARAMS_EN)}
BASE_CATEGORIES = ('Горячее', 'Выпечка', 'Соусы', 'Салаты', 'Соленья',
                   'Варенья')
