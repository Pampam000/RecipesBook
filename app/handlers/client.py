from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from app.keyboards.inline_keyboard import inline_kb_category
from app.keyboards.keyboard import cancel_keyboard
from .decorators import get_chat_id, capitalize_message
from .states_groups import Category
from ..create_bot import bot
from ..create_logger import logger
from ..db import crud


@get_chat_id
async def start(chat_id: int, message: Message):
    logger.info(f"Пользователь {chat_id} Запустил бота")
    await message.answer('Привет!',
                         reply_markup=await crud.get_user_keyboard(chat_id))


@get_chat_id
async def get_all_recipes(chat_id: int, message: Message):
    logger.info(f"Пользователь {chat_id} нажал кнопку 'Список рецептов'")
    await message.answer(await crud.get_all_recipes())


@get_chat_id
async def choose_start(chat_id: int, message: Message):
    await Category.name.set()
    logger.info(f"Пользователь {chat_id} нажал кнопку 'Рецепты по категориям'")
    await message.answer('Укажите категорию', reply_markup=inline_kb_category)
    await message.answer('Или введите вручную', reply_markup=cancel_keyboard)


async def choose_category_callback(callback: CallbackQuery):
    await _choose_category(callback.message, callback.data)
    await callback.answer()


@capitalize_message()
async def choose_category_message(msg_text: str, message: Message):
    await _choose_category(message, msg_text)


@get_chat_id
@capitalize_message(1)
async def get_one_recipe(msg_text: str, chat_id: int, message: Message):
    logger.info(f"Пользователь {chat_id} написал боту '{msg_text}'")
    result = await crud.get_one_recipe(msg_text)
    if result.photo_id:
        await bot.send_photo(chat_id, **await result.as_tg_photo())
    else:
        await message.answer(**await result.as_tg_answ())


@get_chat_id
async def _choose_category(chat_id: int, message: Message, msg_text: str):
    logger.info(f"Пользователь {chat_id} выбрал категорию '{msg_text}'")
    await message.answer(await crud.get_all_recipes_in_category(msg_text))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state=None)
    dp.register_message_handler(get_all_recipes, content_types="text",
                                text='Список рецептов')
    dp.register_message_handler(choose_start, content_types="text",
                                text='Рецепты по категориям')
    dp.register_callback_query_handler(choose_category_callback,
                                       state=Category.name)
    dp.register_message_handler(choose_category_message, state=Category.name,
                                content_types='text')
    dp.register_message_handler(get_one_recipe, content_types="text")
