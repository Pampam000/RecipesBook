from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from app.keyboards.inline_keyboard import inline_kb_category, categories
from app.keyboards.keyboard import admin_keyboard, client_keyboard, \
    cancel_keyboard
from .states_groups import Category
from ..config import ADMINS_ID
from ..create_bot import bot
from ..create_logger import logger
from ..db import crud


async def start(message: Message):
    chat_id = message.from_user.id
    user_keyboard = admin_keyboard if str(chat_id) in ADMINS_ID \
        else client_keyboard
    logger.info(f"Пользователь {chat_id} Запустил бота")
    await message.answer('Привет!', reply_markup=user_keyboard)


async def create_message_with_recipes_list(message: Message, recipes: list):
    result = ''
    for n, i in enumerate(recipes):
        result += f"{n + 1}. {i.name}\n"
    await message.answer(result)


async def get_all_names(message: Message):
    logger.info("Пользователь нажал кнопку 'Список рецептов'")
    if all_recipes := await crud.get_all():
        await create_message_with_recipes_list(message, all_recipes)
    else:
        await message.answer("Список рецептов пуст :(")


async def choose_start(message: Message):
    await Category.category.set()
    logger.info("Пользователь нажал кнопку 'Рецепты по категориям'")
    await message.answer('Укажите категорию', reply_markup=inline_kb_category)
    await message.answer('Или введите вручную', reply_markup=cancel_keyboard)


async def choose_category(callback: CallbackQuery):
    logger.info(f"Пользователь выбрал категорию '{callback.data}'")
    if recipes := await crud.get_all_in_category(callback.data):
        await create_message_with_recipes_list(callback.message, recipes)
    else:
        msg = f"Список рецептов в категории '{callback.data}' пуст :("
        await callback.message.answer(msg)
        logger.info(msg)

    await callback.answer()


async def category_choose(message: Message):
    logger.info(f"Пользователь выбрал категорию '{message.text}'")
    msg_text = message.text.capitalize()
    if msg_text in categories:

        if recipes := await crud.get_all_in_category(msg_text):
            await create_message_with_recipes_list(message, recipes)
        else:
            msg = f"Список рецептов в категории '{msg_text}' пуст :("
            await message.answer(msg)
            logger.info(msg)
    else:
        await message.answer(
            f"Категории '{message.text}' не сущесвует. "
            f"Введите название ещё раз")


async def get_one_recipe(message: Message):
    logger.info(f"Пользователь написал боту '{message.text}'")
    if recipe := await crud.get_one_recipe(message.text.capitalize()):
        await bot.send_photo(message.from_user.id, recipe.photo_id,
                             f'{recipe.name.capitalize()} '
                             f'({recipe.category})\n\n '
                             f'{recipe.ingridients}\n\n {recipe.description}')
    else:
        await message.answer('Нет рецепта с таким названием')


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(get_all_names, content_types="text",
                                text='Список рецептов')
    dp.register_message_handler(choose_start, content_types="text",
                                text='Рецепты по категориям')
    dp.register_callback_query_handler(choose_category,
                                       state=Category.category)
    dp.register_message_handler(category_choose, state=Category.category,
                                content_types='text')
    dp.register_message_handler(get_one_recipe, content_types="text")
