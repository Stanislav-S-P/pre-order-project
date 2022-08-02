"""
Файл с хэндлерами старт/хэлп и регистрация
"""


from aiogram import types, Dispatcher
from database.models import *
from keyboards.keyboards import admin_keyboard, user_keyboard
from loader import bot, logger
from settings import constants


async def start_command(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает команду /start
    :param message: Message
    :return: None
    """
    try:
        with db:
            profile = Profile.get_or_none(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    keyboard = admin_keyboard()
                elif profile.role == 'поставщик':
                    keyboard = None
            except AttributeError:
                keyboard = user_keyboard()
            await bot.send_message(message.from_user.id, constants.WELCOME, reply_markup=keyboard)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def help_command(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает команду /help
    :param message: Message
    :return: None
    """
    try:
        with db:
            try:
                profile = Profile.get_or_none(Profile.user_id == message.from_user.id)
                if profile.role == 'администратор':
                    text = constants.HELP_ADMIN
                elif profile.role == 'поставщик':
                    text = constants.HELP_PROVIDER
            except AttributeError:
                text = constants.HELP_USER
            await bot.send_message(message.from_user.id, text)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_start_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирующая все хэндлеры файла
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_message_handler(help_command, commands=['help'], state=None)
