from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import key_text


def admin_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура - меню администратора
    :return: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    return keyboard.add(
        KeyboardButton(text=key_text.OPEN_PRE_ORDER),
        KeyboardButton(text=key_text.CLOSE_PRE_ORDER),
        KeyboardButton(text=key_text.EXCHANGE_RATE),
        KeyboardButton(text=key_text.MARGIN),
        KeyboardButton(text=key_text.STATUS_PRE_ORDER),
        KeyboardButton(text=key_text.SEND_MESSAGE),
        KeyboardButton(text=key_text.PRODUCT),
        KeyboardButton(text=key_text.MY_PRE_ORDER),
        KeyboardButton(text=key_text.MY_SHOPPING_CART),
        KeyboardButton(text=key_text.PLACE_A_PRE_ORDER),
        KeyboardButton(text=key_text.GROUP),
        KeyboardButton(text=key_text.PROVIDER_HANDLER),
    )


def closing_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура - Подтверждение закрытия предзаказа
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.YES, callback_data=key_text.YES),
        InlineKeyboardButton(text=key_text.NO, callback_data=key_text.NO),
    )


def user_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура - меню пользователя
    :return: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    return keyboard.add(
        KeyboardButton(text=key_text.PRODUCT),
        KeyboardButton(text=key_text.MY_PRE_ORDER),
        KeyboardButton(text=key_text.MY_SHOPPING_CART),
        KeyboardButton(text=key_text.PLACE_A_PRE_ORDER)
    )


def quantity_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура - Выбор количества товара
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.WHOLE, callback_data=key_text.WHOLE),
        InlineKeyboardButton(text=key_text.HALF, callback_data=key_text.HALF),
    )


def order_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура - Добавление товара в корзину
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=key_text.IN_SHOPPING_CART, callback_data=product_id)
    )
    return keyboard


def delete_keyboard(cart_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура - Удаление товара из корзины
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=key_text.DELETE, callback_data=cart_id)
    )
    return keyboard


def confirm_keyboard(request_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура - Подтверждение целых бобин в заказе
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.CONFIRM, callback_data=key_text.YES + ' ' + request_id),
        InlineKeyboardButton(text=key_text.DO_NOT_CONFIRM, callback_data=key_text.NO + ' ' + request_id),
    )


def status_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура - Выбор статуса заявки
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.FIRST_STATUS, callback_data=key_text.FIRST_STATUS),
        InlineKeyboardButton(text=key_text.SECOND_STATUS, callback_data=key_text.SECOND_STATUS),
        InlineKeyboardButton(text=key_text.THIRD_STATUS, callback_data=key_text.THIRD_STATUS),
    )


def confirm_half_keyboard(first_id: str, second_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура - Подтверждение половинок бобин в заказе
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.CONFIRM, callback_data=key_text.YES2 + ' ' + first_id + ' ' + second_id),
        InlineKeyboardButton(
            text=key_text.DO_NOT_CONFIRM, callback_data=key_text.NO2 + ' ' + first_id + ' ' + second_id
        ),
    )
