from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.create_logger import logger
from app.keyboards.inline_keyboard import inline_kb_update
from app.keyboards.keyboard import cancel_keyboard, admin_keyboard
from .states_groups import Load, Update, Delete, Category
from ..db import crud


async def other_text(message: Message, state: FSMContext):
    state_str = await state.get_state()
    logger.info(f'Пользователь ввёл НЕ текстовое сообщение для состояния: '
                f'{state_str}\n Сообщение: {message}')

    if state_str:
        await message.reply('Пожалуйста, введите текстовое сообщение',
                            reply_markup=cancel_keyboard)
    else:
        await message.reply('Пожалуйста, введите текстовое сообщение',
                            reply_markup=admin_keyboard)


async def other_callback(message: Message, state: FSMContext):
    state_str = await state.get_state()
    logger.info(f'Пользователь ввёл НЕ текстовое сообщение для состояния: '
                f'{state_str}\n и НЕ нажал кнопку. '
                f'Сообщение: {message}')

    if state_str == 'Update:what_to_change':
        await message.reply(
            'Пожалуйста, введите текстовое сообщение или нажмите кнопку',
            reply_markup=inline_kb_update)
    else:  # elif state_str in ('Category:category', 'Update:change_category')
        await message.reply(
            'Пожалуйста, введите текстовое сообщение или нажмите кнопку',
            reply_markup=await crud.create_inline_kb_categories)


async def other_photo(message: Message, state: FSMContext):
    logger.info(f'Пользователь НЕ загрузил фото для:'
                f' {await state.get_state()}\n Сообщение: {message}')
    await message.reply('Пожалуйста, загрузите фото',
                        reply_markup=cancel_keyboard)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(other_photo, content_types='any',
                                state=[Load.photo, Update.change_photo])
    dp.register_message_handler(other_callback, content_types='any',
                                state=[Category.name,
                                       Update.what_to_change,
                                       Update.change_category])
    dp.register_message_handler(other_text, content_types='any',
                                state=Load.states_names + Update.states_names
                                      + Delete.states_names + (
                                          None,))
