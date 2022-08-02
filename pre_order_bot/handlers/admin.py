import re
from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from database.state import FSMOpen, FSMClose, FSMExchangeRate, FSMMargin, FSMMessage
from handlers import start
from handlers.user import product_handler, my_pre_order_handler, my_cart_handler, place_a_pre_order_handler
from keyboards import key_text
from database.models import *
from keyboards.keyboards import closing_keyboard, status_keyboard, confirm_half_keyboard, confirm_keyboard
from loader import bot, logger
from settings import constants
from settings.settings import CHANNEL_ID


async def opening_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки OPEN_PRE_ORDER. Входит в машину состояния.
    :param message:Message
    :return:None
    """
    try:
        with db:
            profile = Profile.get(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    pre_order = PreOrder.get_or_none(PreOrder.status == 'Открыт')
                    if pre_order:
                        await bot.send_message(message.from_user.id, constants.ALREADY_OPEN)
                    else:
                        await FSMOpen.title.set()
                        await bot.send_message(message.from_user.id, constants.TITLE_PRE_ORDER)
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def title_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние title. Закрывает машину состояния и открывает предзаказ.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        with db:
            PreOrder(name=message.text, status='Открыт', opening_date=datetime.today()).save()
        await bot.send_message(message.from_user.id, constants.OPEN_PRE_ORDER)
        await bot.send_message(CHANNEL_ID, constants.OPEN_PRE_ORDER)
        await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def closing_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки CLOSE_PRE_ORDER. Входит в машину состояния.
    :param message:Message
    :return:None
    """
    try:
        with db:
            profile = Profile.get_or_none(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    pre_order = PreOrder.select().where(PreOrder.status == 'Открыт')
                    if pre_order:
                        await FSMClose.confirm.set()
                        await bot.send_message(
                            message.from_user.id, constants.PRE_ORDER_CONFIRM, reply_markup=closing_keyboard()
                        )
                    else:
                        await bot.send_message(message.from_user.id, constants.NO_ACTIVE_PRE_ORDER)
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def confirm_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние confirm. Закрывает машину состояния и закрывает предзаказ.
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        if call.data == key_text.YES:
            with db:
                PreOrder.update(
                    {PreOrder.status: 'Закрыт', PreOrder.closing_date: datetime.today()}
                ).where(PreOrder.status == 'Открыт').execute()
            await bot.edit_message_text(
                chat_id=call.from_user.id, message_id=call.message.message_id, text=constants.CLOSE_PRE_ORDER
            )
            await bot.send_message(CHANNEL_ID, constants.CLOSE_PRE_ORDER)
        await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def exchange_rate_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки EXCHANGE_RATE. Входит в машину состояния.
    :param message:Message
    :return:None
    """
    try:
        with db:
            profile = Profile.get_or_none(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    get_rate = AdminPanel.get(AdminPanel.key == 'Курс')
                    await FSMExchangeRate.rate.set()
                    await bot.send_message(message.from_user.id, constants.CURRENT_RATE.format(get_rate.value))
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def rate_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние rate. Закрывает машину состояния и меняет курс.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if [message.text] == re.findall(r'\d+[.,]\d+', message.text):
            if [message.text] == re.findall(r'\d+[,]\d+', message.text):
                new_rate = re.sub(r'[,]', '.', message.text)
            else:
                new_rate = message.text
            AdminPanel.update({AdminPanel.value: new_rate}).where(AdminPanel.key == 'Курс').execute()
            margin = AdminPanel.get(AdminPanel.key == 'Маржа').value
            products = Product.select()
            for product in products:
                price = round(float(product.price) * float(message.text), 2)
                correct_price = round(price / 100 * margin + price, 2)
                Product.update({Product.correct_price: correct_price}).where(Product.id == product.id).execute()
            await bot.send_message(message.from_user.id, constants.COMPLETE_RATE)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_NUMBER)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def margin_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки MARGIN. Входит в машину состояния.
    :param message:Message
    :return:None
    """
    try:
        with db:
            profile = Profile.get(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    get_margin = AdminPanel.get(AdminPanel.key == 'Маржа')
                    await FSMMargin.margin.set()
                    await bot.send_message(message.from_user.id, constants.CURRENT_MARGIN.format(get_margin.value))
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def margin_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние margin. Закрывает машину состояния и меняет маржу.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if [message.text] == re.findall(r'\d+[.,]\d+', message.text):
            if [message.text] == re.findall(r'\d+[,]\d+', message.text):
                new_margin = re.sub(r'[,]', '.', message.text)
            else:
                new_margin = message.text
            AdminPanel.update({AdminPanel.value: new_margin}).where(AdminPanel.key == 'Маржа').execute()
            rate = AdminPanel.get(AdminPanel.key == 'Курс').value
            products = Product.select()
            for product in products:
                price = round(float(product.price) * float(rate), 2)
                correct_price = round(price / 100 * float(message.text) + price, 2)
                Product.update({Product.correct_price: correct_price}).where(Product.id == product.id).execute()
            await bot.send_message(message.from_user.id, constants.COMPLETE_MARGIN)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_NUMBER)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def status_pre_order(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки STATUS_PRE_ORDER. Отправляет клавиатуру выбора статуса.
    :param message:Message
    :return:None
    """
    try:
        with db:
            profile = Profile.get(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    await bot.send_message(
                        message.from_user.id, constants.CHOICE_STATUS, reply_markup=status_keyboard()
                    )
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def first_status(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки статуса -Новая. Выводит все заявки в данном статусе.
    :param call:CallbackQuery
    :return:None
    """
    try:
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
        requests_user = Request.select().where(Request.status == 'Новая')
        for request_user in requests_user:
            await bot.send_photo(
                call.from_user.id,
                photo=open('../pre_order/media/' + request_user.color_number.image_id, 'rb'),
                caption=constants.CART_TEMPLATE.format(
                    request_user.product.name, request_user.product.correct_structure,
                    request_user.product.footage, request_user.product.correct_price, request_user.quantity
                ))
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        await bot.send_message(call.from_user.id, constants.EMPTY_STATUS)


async def second_status(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки статуса -Подтверждена. Выводит все заявки в данном статусе.
    :param call:CallbackQuery
    :return:None
    """
    try:
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
        requests_user = Request.select().where(Request.status == 'Подтверждена')
        for request_user in requests_user:
            await bot.send_photo(
                call.from_user.id,
                photo=open('../pre_order/media/' + request_user.color_number.image_id, 'rb'),
                caption=constants.CART_TEMPLATE.format(
                    request_user.product.name, request_user.product.correct_structure,
                    request_user.product.footage, request_user.product.correct_price, request_user.quantity
                ))
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        await bot.send_message(call.from_user.id, constants.EMPTY_STATUS)


async def third_status(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки статуса -Не подтверждена. Выводит все заявки в данном статусе.
    :param call:CallbackQuery
    :return:None
    """
    try:
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)
        requests_user = Request.select().where(Request.status == 'Не подтверждена')
        if requests_user:
            for request_user in requests_user:
                await bot.send_photo(
                    call.from_user.id,
                    photo=open('../pre_order/media/' + request_user.color_number.image_id, 'rb'),
                    caption=constants.CART_TEMPLATE.format(
                        request_user.product.name, request_user.product.correct_structure,
                        request_user.product.footage, request_user.product.correct_price, request_user.quantity
                    ))
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        await bot.send_message(call.from_user.id, constants.EMPTY_STATUS)


async def send_message_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки SEND_MESSAGE. Входит в машину состояния.
    :param message:Message
    :return:None
    """
    try:
        with db:
            profile = Profile.get(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    await FSMMessage.mess.set()
                    await bot.send_message(message.from_user.id, constants.MESSAGE_TEXT)
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def mess_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние mess. Закрывает машину состояния и отправляет введенное сообщение в канал.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        await bot.send_message(CHANNEL_ID, message.text)
        await state.finish()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def group_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает  кнопку GROUP. Группирует половинки бобин и отправляет на подтверждение заявки поставщику.
    :param message: Message
    :return: None
    """
    try:
        color_numbers = ColorNumber.select()
        flag = False
        for color_number in color_numbers:
            request_user = Request.select().where(
                Request.status == 'Новая', Request.quantity == 'Половина',
                Request.product == color_number.product, Request.color_number == color_number.id
            )
            if len(request_user) > 1:
                provider = Profile.get(Profile.role == 'поставщик')
                request_list = []
                for elem in request_user:
                    request_list.append(elem)
                    if len(request_list) == 2:
                        await bot.send_photo(
                            provider.user_id, photo=open('../pre_order/media/' + elem.color_number.image_id, 'rb'),
                            caption=constants.CART_TEMPLATE_PR.format(
                                elem.product.name, elem.product.correct_structure,
                                elem.product.footage, elem.product.price, 'Целая'
                            ),
                            reply_markup=confirm_half_keyboard(str(request_list[0].id), str(elem.id))
                        )
                        request_list = []
                        flag = True
        if flag:
            await bot.send_message(message.from_user.id, constants.GROUP_COMPLETE)
        else:
            await bot.send_message(message.from_user.id, constants.GROUP_EMPTY)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def provider_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает  кнопку PROVIDER_HANDLER. Отправляет на подтверждение заявки поставщику.
    :param message: Message
    :return: None
    """
    try:
        requests_user = Request.select().where(Request.status == 'Новая')
        if len(requests_user) != 0:
            for request in requests_user:
                provider = Profile.get(Profile.role == 'поставщик')
                await bot.send_photo(
                    provider.user_id, photo=open('../pre_order/media/' + request.color_number.image_id, 'rb'),
                    caption=constants.CART_TEMPLATE_PR.format(
                        request.product.name, request.product.correct_structure,
                        request.product.footage, request.product.price, request.quantity
                    ),
                    reply_markup=confirm_keyboard(str(request.id))
                )
        else:
            await bot.send_message(message.from_user.id, constants.EMPTY_HALF_REQUEST)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def cancel_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - позволяет выйти из машины состояния
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        if message.text == '/start':
            await start.start_command(message)
        elif message.text == '/help':
            await start.help_command(message)
        elif message.text == key_text.OPEN_PRE_ORDER:
            await opening_handler(message)
        elif message.text == key_text.CLOSE_PRE_ORDER:
            await closing_handler(message)
        elif message.text == key_text.EXCHANGE_RATE:
            await exchange_rate_handler(message)
        elif message.text == key_text.MARGIN:
            await margin_handler(message)
        elif message.text == key_text.STATUS_PRE_ORDER:
            await status_pre_order(message)
        elif message.text == key_text.SEND_MESSAGE:
            await send_message_handler(message)
        elif message.text == key_text.PRODUCT:
            await product_handler(message)
        elif message.text == key_text.MY_PRE_ORDER:
            await my_pre_order_handler(message)
        elif message.text == key_text.MY_SHOPPING_CART:
            await my_cart_handler(message)
        elif message.text == key_text.PLACE_A_PRE_ORDER:
            await place_a_pre_order_handler(message)
        elif message.text == key_text.PROVIDER_HANDLER:
            await provider_handler(message)
        elif message.text == key_text.GROUP:
            await group_handler(message)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_admin_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирующая все хэндлеры файла
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(
        cancel_state, lambda message: message.text in [
            '/start', '/help', key_text.OPEN_PRE_ORDER, key_text.CLOSE_PRE_ORDER, key_text.EXCHANGE_RATE,
            key_text.MARGIN, key_text.STATUS_PRE_ORDER, key_text.SEND_MESSAGE, key_text.PRODUCT,
            key_text.MY_PRE_ORDER, key_text.MY_SHOPPING_CART, key_text.PLACE_A_PRE_ORDER
        ], state='*'
    )
    dp.register_message_handler(opening_handler, lambda message: message.text == key_text.OPEN_PRE_ORDER, state=None)
    dp.register_message_handler(title_state, content_types=['text'], state=FSMOpen.title)
    dp.register_message_handler(closing_handler, lambda message: message.text == key_text.CLOSE_PRE_ORDER, state=None)
    dp.register_callback_query_handler(confirm_state, lambda call: call.data == key_text.YES, state=FSMClose.confirm)
    dp.register_message_handler(
        exchange_rate_handler, lambda message: message.text == key_text.EXCHANGE_RATE, state=None
    )
    dp.register_message_handler(rate_state, content_types=['text'], state=FSMExchangeRate.rate)
    dp.register_message_handler(margin_handler, lambda message: message.text == key_text.MARGIN, state=None)
    dp.register_message_handler(margin_state, content_types=['text'], state=FSMMargin.margin)
    dp.register_message_handler(status_pre_order, lambda message: message.text == key_text.STATUS_PRE_ORDER, state=None)
    dp.register_message_handler(send_message_handler, lambda message: message.text == key_text.SEND_MESSAGE, state=None)
    dp.register_message_handler(mess_state, content_types=['text'], state=FSMMessage.mess)
    dp.register_callback_query_handler(first_status, lambda call: call.data == key_text.FIRST_STATUS, state=None)
    dp.register_callback_query_handler(second_status, lambda call: call.data == key_text.SECOND_STATUS, state=None)
    dp.register_callback_query_handler(third_status, lambda call: call.data == key_text.THIRD_STATUS, state=None)
    dp.register_message_handler(group_handler, lambda message: message.text == key_text.GROUP, state=None)
    dp.register_message_handler(provider_handler, lambda message: message.text == key_text.PROVIDER_HANDLER, state=None)
