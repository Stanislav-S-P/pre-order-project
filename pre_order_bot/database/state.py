"""
Файл с моделями машины состояний
"""


from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMOpen(StatesGroup):
    title = State()


class FSMClose(StatesGroup):
    confirm = State()


class FSMExchangeRate(StatesGroup):
    rate = State()


class FSMMargin(StatesGroup):
    margin = State()


class FSMMessage(StatesGroup):
    mess = State()


class FSMProduct(StatesGroup):
    color_number = State()
    quantity = State()


class FSMOrder(StatesGroup):
    full_name = State()
    phone = State()
    address = State()
    comment = State()
