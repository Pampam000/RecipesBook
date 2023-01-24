from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from app.keyboards.inline_keyboard import inline_kb_category
from app.keyboards.keyboard import admin_keyboard, client_keyboard
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


async def get_all_names(message: Message):
    logger.info("Пользователь нажал кнопку 'Список рецептов'")
    if all_recipes := await crud.get_all():
        result = ''

        for n, i in enumerate(all_recipes):
            result += f"{n + 1}. {i.name}\n"

        await message.answer(result)
    else:
        await message.answer("Список рецептов пуст :(")


async def get_recipes_by_category(message: Message):
    logger.info("Пользователь нажал кнопку 'Рецепты по категориям'")
    await message.answer('Укажите категорию', reply_markup=inline_kb_category)


async def choose_category(callback: CallbackQuery):
    logger.info(f"Пользователь выбрал категорию '{callback.data}'")
    if recipes := await crud.get_all_in_category(callback.data):
        result = ''

        for n, i in enumerate(recipes):
            result += f"{n + 1}. {i.name}\n"

        await callback.message.answer(result)

    else:
        msg = f"Список рецептов в категории '{callback.data}' пуст :("
        await callback.message.answer(msg)
        logger.info(msg)

    await callback.answer()


async def get_one_recipe(message: Message):
    logger.info(f"Пользователь написал боту '{message.text}'")
    if recipe := await crud.get_one_recipe(message.text.capitalize()):

        await bot.send_photo(message.from_user.id, recipe.photo_id,
                             f'{recipe.name.capitalize()} '
                             f'({recipe.category})\n\n '
                             f'{recipe.ingridients}\n\n {recipe.description}')
    else:
        await message.answer('Нет рецепта с таким названием')


async def other(message: Message):
    logger.info("Пользователь ввёл НЕ текстовое сообщение для поиска "
                f"рецепта: {message.values}")
    await message.answer("Для корректной работы, пожалуйста, введите текст")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(get_all_names, content_types="text",
                                text=['Список рецептов'])
    dp.register_message_handler(get_recipes_by_category, content_types="text",
                                text=['Рецепты по категориям'])
    dp.register_callback_query_handler(
        choose_category)
    dp.register_message_handler(get_one_recipe, content_types="text")
    dp.register_message_handler(other, content_types='any')
