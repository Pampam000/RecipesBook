from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from ..config import ADMINS_ID
from ..create_bot import bot
from ..db import crud
from ..keyboards.inline_keyboard import inline_kb_category, inline_kb_update
from ..keyboards.keyboard import cancel_keyboard, admin_keyboard


class Load(StatesGroup):
    name = State()
    category = State()
    ingridients = State()
    description = State()
    photo = State()


class Delete(StatesGroup):
    name = State()


class Update(StatesGroup):
    name = State()
    what_to_change = State()
    new_value = State()


async def load_start(message: Message):
    if str(message.from_user.id) in ADMINS_ID:
        await Load.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
    else:
        await message.reply("Вы не можете загружать рецепты")


async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        await message.answer("Нечего отменять")
        return
    await state.finish()
    await message.answer('Действие отменено', reply_markup=admin_keyboard)


async def set_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if await crud.get_one_recipe(message.text):
            await message.answer("Рецепт с таким названием уже существует, "
                                 "введите другое название",
                                 reply_markup=cancel_keyboard)
        else:
            data['name'] = message.text.capitalize()
            await Load.next()
            await message.answer("Укажите категорию",
                                 reply_markup=inline_kb_category)


async def choose_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = callback.data
    await Load.next()
    await callback.message.answer("Введите список ингридиентов",
                                  reply_markup=cancel_keyboard)
    await callback.answer()


async def set_ingridients(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ingridients'] = message.text
    await Load.next()
    await message.answer("Введите описание")


async def set_description(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await Load.next()
    await message.answer("Загрузите фото")


async def set_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_id'] = message.photo[-1].file_id

        msg = await crud.add_to_db(data)
        await message.answer(msg, reply_markup=admin_keyboard)

    await state.finish()


async def delete_start(message: Message):
    if str(message.from_user.id) in ADMINS_ID:
        await Delete.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
    else:
        await message.reply("Вы не можете удалять рецепты")


async def delete(message: Message, state: FSMContext):
    if await crud.delete_recipe(message.text):
        await message.answer(
            f"Рецепт '{message.text}' удалён успешно",
            reply_markup=admin_keyboard)
        await state.finish()
    else:
        await message.answer(f"Рецепт '{message.text}' не найден",
                             reply_markup=cancel_keyboard)


async def update_start(message: Message):
    if str(message.from_user.id) in ADMINS_ID:
        await Update.name.set()
        await message.answer("Введите название", reply_markup=cancel_keyboard)
    else:
        await message.reply("Вы не можете обновлять рецепты")


async def update(message: Message, state: FSMContext):
    async with state.proxy() as data:

        if recipe := await crud.get_one_recipe(message.text.capitalize()):
            data['name'] = recipe.name
            await bot.send_photo(message.from_user.id, recipe.photo_id,
                                 f'{recipe.name}'
                                 f' ({recipe.category})\n\n'
                                 f'{recipe.ingridients}\n\n'
                                 f'{recipe.description}')

            await message.answer("Что будем менять?",
                                 reply_markup=inline_kb_update)
            await Update.next()
        else:
            await message.answer(
                'Нет рецепта с таким названием')


async def choose(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['what_to_change'] = callback.data

        if 'category' in callback.data:
            await callback.message.answer("На какую категорию заменить?",
                                          reply_markup=inline_kb_category)
        elif 'photo' in callback.data:
            await callback.message.answer(f"Загрузите новое фото",
                                          reply_markup=cancel_keyboard)
        else:
            await callback.message.answer(f"Введите новое значение",
                                          reply_markup=cancel_keyboard)
        await Update.next()
        await callback.answer()


async def up(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.text.capitalize()
        msg = await crud.update(name=data['name'], key=data['what_to_change'],
                                value=data['value'])
        await message.answer(msg, reply_markup=admin_keyboard)

    await state.finish()


async def up_photo(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.photo[-1].file_id

        msg = await crud.update(name=data['name'], key=data['what_to_change'],
                                value=data['value'])
        await message.answer(msg, reply_markup=admin_keyboard)
        await state.finish()


async def up_category(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = callback.data.capitalize()
        msg = await crud.update(name=data['name'], key=data['what_to_change'],
                                value=data['value'])
        await callback.message.answer(msg, reply_markup=admin_keyboard)
        await state.finish()
        await callback.answer()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(load_start, text=['Загрузить'], state=None)
    dp.register_message_handler(cancel, text=['Отмена'], state="*")
    dp.register_message_handler(set_name, state=Load.name)
    dp.register_callback_query_handler(choose_category,
                                       state=Load.category)
    dp.register_message_handler(set_ingridients, state=Load.ingridients)
    dp.register_message_handler(set_description, state=Load.description)
    dp.register_message_handler(set_photo, content_types=['photo'],
                                state=Load.photo)

    dp.register_message_handler(delete_start, text=['Удалить рецепт'],
                                state=None)
    dp.register_message_handler(delete, state=Delete.name)

    dp.register_message_handler(update_start, text=['Обновить рецепт'],
                                state=None)
    dp.register_message_handler(update, state=Update.name)
    dp.register_callback_query_handler(choose, state=Update.what_to_change)
    dp.register_message_handler(up, content_types=["text"],
                                state=Update.new_value)
    dp.register_message_handler(up_photo, content_types=["photo"],
                                state=Update.new_value)
    dp.register_callback_query_handler(up_category, state=Update.new_value)
    # lambda callback: callback.data.startswith('update')
