from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.create_logger import logger
from app.keyboards.keyboard import cancel_keyboard
from .states_groups import Load, Update, Delete


async def other_text(message: Message, state: FSMContext):
    logger.info(f'Пользователь ввёл НЕ текстовое сообщение для состояния: '
                f'{await state.get_state()}\n Сообщение: {message}')
    await message.reply('Пожалуйста, введите текстовое сообщение',
                        reply_markup=cancel_keyboard)


async def other_photo(message: Message, state: FSMContext):
    logger.info(f'Пользователь НЕ загрузил фото для:'
                f' {await state.get_state()}\n Сообщение: {message}')
    await message.reply('Пожалуйста, загрузите фото',
                        reply_markup=cancel_keyboard)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(other_photo, content_types='any',
                                state=[Load.photo, Update.change_photo])
    dp.register_message_handler(other_text, content_types='any',
                                state=Load.states_names + Update.states_names
                                      + Delete.states_names + (None,))
