from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy
from aiogram.types import Message, CallbackQuery

from app.config import RECIPE_PARAMS
from app.create_bot import bot
from app.create_logger import logger
from app.db import crud
from app.keyboards.keyboard import admin_keyboard
from ..config import WHAT_TO_CHANGE, create_cases
from ..decorators import get_chat_id, capitalize_message, check_what_to_change
from ..states_groups import Update


@get_chat_id
async def update_start(chat_id: int, message: Message):
    result = await crud.update_start(chat_id)

    if result.go_next:
        await Update.name.set()
        await message.answer(**await result.as_tg_answer())
    else:
        await message.reply(**await result.as_tg_answer())


@get_chat_id
@capitalize_message(1)
async def update(msg_text: str, chat_id: int, message: Message,
                 state: FSMContext):
    logger.info(f'Пользователь {chat_id} хочет обновить рецепт: {msg_text}')

    recipe = await crud.get_one_recipe(msg_text)
    if recipe.photo_id:
        async with state.proxy() as data:
            data['name'] = msg_text
        await bot.send_photo(chat_id, **await recipe.as_tg_photo())
        await message.answer(**await WHAT_TO_CHANGE.as_tg_answer())
        await Update.next()
    else:
        await message.answer(**await recipe.as_tg_answ())


async def choose_what_to_change_callback(callback: CallbackQuery,
                                         state: FSMContext):
    await _choose_what_to_change(callback.message, callback.data, state)
    await callback.answer()


@capitalize_message()
@check_what_to_change
async def choose_what_to_change_message(msg_text: str, message: Message,
                                        state: FSMContext):
    await _choose_what_to_change(message, msg_text, state)


@capitalize_message()
async def update_name(msg_text: str, message: Message, state: FSMContext):
    recipe = await crud.get_one_recipe(msg_text)
    if recipe.photo_id:
        await message.answer(f"Рецепт с названием  '{msg_text}' "
                             f"уже существует. Введите другое "
                             f"название.")
        logger.info(f"Рецепт '{msg_text}' уже существует")
    else:
        async with state.proxy() as data:
            data['value'] = msg_text
            await _set_new_value(message, state, data)


@capitalize_message()
async def update_text(msg_text: str, message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = msg_text
        await _set_new_value(message, state, data)


async def up_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.photo[-1].file_id
        await _set_new_value(message, state, data)


async def up_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = callback.data.capitalize()
        await _set_new_value(callback.message, state, data)
        await callback.answer()


async def category_up(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.text.capitalize()
        await _set_new_value(message, state, data)


@get_chat_id
async def _choose_what_to_change(chat_id: int, message: Message, msg: str,
                                 state: FSMContext):
    logger.info(f'Пользователь {chat_id} хочет изменить: {msg}')

    async with state.proxy() as data:
        data['what_to_change'] = RECIPE_PARAMS[msg]
    recipe = await create_cases()
    logger.info(recipe)
    recipe = recipe[msg]
    logger.info(recipe)
    await message.answer(**await recipe.as_tg_answer())
    await recipe.new_state.set()


async def _set_new_value(message: Message, state: FSMContext,
                         data: FSMContextProxy):
    logger.info(f'Новое значение: {data["value"]}')
    msg = await crud.update(data['name'], data['what_to_change'],
                            data['value'])
    await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(f"Конечный автомат {await state.get_state()} закончен")
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(update_start, text='Обновить рецепт',
                                state=None)
    dp.register_message_handler(update, state=Update.name)
    dp.register_callback_query_handler(choose_what_to_change_callback,
                                       state=Update.what_to_change)
    dp.register_message_handler(choose_what_to_change_message,
                                state=Update.what_to_change)
    dp.register_message_handler(update_name, content_types="text",
                                state=Update.change_name)
    dp.register_message_handler(update_text, content_types="text",
                                state=Update.change_text)
    dp.register_message_handler(up_photo, content_types="photo",
                                state=Update.change_photo)
    dp.register_callback_query_handler(up_category,
                                       state=Update.change_category)
    dp.register_message_handler(category_up, state=Update.change_category)
