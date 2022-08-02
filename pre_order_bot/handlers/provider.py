from aiogram import Dispatcher, types
from database.models import *
from keyboards import key_text
from keyboards.keyboards import confirm_keyboard, confirm_half_keyboard
from loader import bot, logger
from settings import constants


async def confirm_handler(call: types.CallbackQuery) -> None:
    """
    Хэндер - обрабатывает нажатие кнопок подтверждения статуса заказа с целыми бобинами.
    :param call: CallbackQuery
    :return: None
    """
    try:
        with db:
            try:
                profile = Profile.get_or_none(Profile.user_id == call.from_user.id)
                if profile.role == 'поставщик':
                    answer, request_id = call.data.split()
                    if answer == key_text.YES:
                        status = 'Подтверждена'
                    else:
                        status = 'Не подтверждена'
                    Request.update({Request.status: status}).where(Request.id == int(request_id)).execute()
                    request = Request.get(Request.id == int(request_id))
                    await bot.send_photo(
                        request.user_id, photo=open('../pre_order/media/' + request.color_number.image_id, 'rb'),
                        caption=constants.NEW_STATUS_PRE_ORDER.format(request.quantity, request.status)
                    )
                    await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                                   caption=constants.TEMPLATE_MEDIA_STATUS.format(
                                                       request.product.name, request.product.correct_structure,
                                                       request.product.footage, request.product.price, request.quantity,
                                                       status
                                                   ), reply_markup=confirm_keyboard(str(request.id)))
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def confirm_half_handler(call: types.CallbackQuery) -> None:
    """
    Хэндер - обрабатывает нажатие кнопок подтверждения статуса заказа с половиной бобины.
    :param call: CallbackQuery
    :return: None
    """
    try:
        with db:
            try:
                profile = Profile.get_or_none(Profile.user_id == call.from_user.id)
                if profile.role == 'поставщик':
                    answer, first_id, second_id = call.data.split()
                    if answer == key_text.YES2:
                        status = 'Подтверждена'
                    else:
                        status = 'Не подтверждена'
                    for request_id in [first_id, second_id]:
                        Request.update({Request.status: status}).where(Request.id == int(request_id)).execute()
                        request = Request.get(Request.id == int(request_id))
                        await bot.send_photo(
                            request.user_id, photo=open('../pre_order/media/' + request.color_number.image_id, 'rb'),
                            caption=constants.NEW_STATUS_PRE_ORDER.format(request.quantity, request.status)
                        )
                    await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                                   caption=constants.TEMPLATE_MEDIA_STATUS.format(
                                                       request.product.name, request.product.correct_structure,
                                                       request.product.footage, request.product.price, request.quantity,
                                                       status
                                                   ), reply_markup=confirm_half_keyboard(first_id, second_id))
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_provider_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирующая все хэндлеры файла
    :param dp: Dispatcher
    :return: None
    """
    dp.register_callback_query_handler(
        confirm_handler, lambda call: call.data.split()[0] in [key_text.YES, key_text.NO], state=None
    )
    dp.register_callback_query_handler(
        confirm_half_handler, lambda call: call.data.split()[0] in [key_text.YES2, key_text.NO2], state=None
    )
