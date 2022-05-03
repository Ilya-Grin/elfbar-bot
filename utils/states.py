from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    start = State()
    getting = State()
    phone = State()
    admin = State()
    setbars = State()
    complite = State()
