from aiogram.dispatcher.filters.state import State, StatesGroup


class Load(StatesGroup):
    name = State()
    category = State()
    ingridients = State()
    description = State()
    photo = State()


class Update(StatesGroup):
    name = State()
    what_to_change = State()
    change_text = State()
    change_photo = State()


class Delete(StatesGroup):
    name = State()
