from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from app.config import ADMINS_ID
from app.create_bot import dp
from app.create_logger import logger
from app.db import crud
from app.keyboards.inline_keyboard import inline_kb_category
from app.keyboards.keyboard import cancel_keyboard, admin_keyboard


class Load(StatesGroup):
    name = State()
    category = State()
    ingridients = State()
    description = State()
    photo = State()


async def load_start(message: Message):
    user_id = message.from_user.id
    if str(user_id) in ADMINS_ID:

        await Load.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
        logger.info(f'Пользователь с id {user_id} является админом и начал '
                    'загрузку рецепта')
    else:
        await message.reply("Вы не можете загружать рецепты")
        logger.info(f'Пользователь с id {user_id} НЕ является админом и хотел '
                    'начать загрузку рецепта')


async def set_name(message: Message, state: FSMContext):
    logger.info(f'Пользователь хочет создать рецепт: {message.text}')
    if await crud.get_one_recipe(message.text):
        await message.answer(f"Рецепт c названием: '{message.text}' уже "
                             f"существует, введите другое название",
                             reply_markup=cancel_keyboard)
        logger.info('Такой рецепт уже существует')
    else:
        async with state.proxy() as data:
            data['name'] = message.text.capitalize()
            await Load.next()
            await message.answer("Укажите категорию",
                                 reply_markup=inline_kb_category)
            logger.info(f'Пользователь успешно указал название рецепта: '
                        f'{message.text}')


async def choose_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = callback.data
        logger.info(
            f"Пользователь выбрал категорию '{callback.data}' для рецепта: "
            f" {data['name']}")
    await Load.next()
    await callback.message.answer("Введите список ингридиентов",
                                  reply_markup=cancel_keyboard)
    await callback.answer()


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
        msg = await crud.add_to_db(data)
        await message.answer(msg, reply_markup=admin_keyboard)
    logger.info(f"Конечный автомат {await state.get_state()} закончен")
    await state.finish()


def register_handlers():
    dp.register_message_handler(load_start, text=['Загрузить'], state=None)

    dp.register_message_handler(set_name, state=Load.name)
    dp.register_callback_query_handler(choose_category,
                                       state=Load.category)
    dp.register_message_handler(set_ingridients, state=Load.ingridients)
    dp.register_message_handler(set_description, state=Load.description)
    dp.register_message_handler(set_photo, content_types=['photo'],
                                state=Load.photo)
