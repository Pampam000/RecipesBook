from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from app.create_logger import logger
from app.db import crud
from app.keyboards.keyboard import cancel_keyboard, admin_keyboard
from ..decorators import get_chat_id, capitalize_message
from ..states_groups import Load


@get_chat_id
async def load_start(chat_id: int, message: Message):
    result = await crud.load_start(chat_id)

    if result.go_next:
        await Load.name.set()
        await message.answer(**await result.as_tg_answer())
    else:
        await message.reply(result.text)


@get_chat_id
@capitalize_message(1)
async def set_name(msg_text: str, chat_id: int, message: Message,
                   state: FSMContext):
    logger.info(f'Пользователь {chat_id} хочет создать рецепт: {msg_text}')
    result = await crud.check_recipe_name_in_db(msg_text)
    await message.answer(**await result.as_tg_answer())
    if result.go_next:
        async with state.proxy() as data:
            data['name'] = msg_text
        await Load.next()
        await message.answer("Или введите вручную")
        logger.info(f'Пользователь успешно указал название рецепта: '
                    f'{msg_text}')


async def choose_category_callback(callback: CallbackQuery, state: FSMContext):
    await _choose_category(callback.message, callback.data, state)
    await callback.answer()


@capitalize_message()
async def choose_category_message(msg_text: str, message: Message,
                                  state: FSMContext):
    await _choose_category(message, msg_text, state)


async def set_ingridients(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ingridients'] = message.text
        logger.info(
            f"Пользователь указал ингридиенты '{message.text}' для рецепта: "
            f" {data['name']}")
    await Load.next()
    await message.answer("Введите описание")


async def set_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        logger.info(
            f"Пользователь указал описание '{message.text}' для рецепта: "
            f" {data['name']}")
    await Load.next()
    await message.answer("Загрузите фото")


async def set_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        photo_id = message.photo[-1].file_id
        data['photo_id'] = photo_id
        logger.info(
            f"Пользователь установил фото '{photo_id}' для рецепта: "
            f" {data['name']}")
        msg = await crud.add_recipe(data)
        await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(f"Конечный автомат {await state.get_state()} закончен")
    await state.finish()


@get_chat_id
async def _choose_category(chat_id: int, message: Message, msg_text: str,
                           state: FSMContext):
    async with state.proxy() as data:
        data['category'] = msg_text
        logger.info(f"Пользователь {chat_id} выбрал категорию '{msg_text}' "
                    f"для рецепта \'{data['name']}\'")
    await Load.next()
    await message.answer("Введите список ингридиентов",
                         reply_markup=cancel_keyboard)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(load_start, text='Загрузить', state=None)
    dp.register_message_handler(set_name, content_types='text',
                                state=Load.name)
    dp.register_callback_query_handler(choose_category_callback,
                                       state=Load.category)
    dp.register_message_handler(choose_category_message, content_types='text',
                                state=Load.category)
    dp.register_message_handler(set_ingridients, state=Load.ingridients)
    dp.register_message_handler(set_description, state=Load.description)
    dp.register_message_handler(set_photo, content_types='photo',
                                state=Load.photo)
