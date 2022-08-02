import re
from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from database.models import *
from database.state import FSMOrder, FSMProduct
from handlers import start
from keyboards import key_text
from keyboards.keyboards import order_keyboard, quantity_keyboard, delete_keyboard, confirm_keyboard
from loader import bot, logger
from settings import constants


async def product_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает кнопку PRODUCT
    :param message: Message
    :return: None
    """
    try:
        products = Product.select()
        for product in products:
            color_numbers = ColorNumber.select().where(ColorNumber.product == product.id)
            media_massive = []
            for index, color_number in enumerate(color_numbers):
                media_massive.append(InputMediaPhoto(open('../pre_order/media/' + color_number.image_id, 'rb')))
                if index == 9:
                    break
            await bot.send_media_group(message.from_user.id, media=media_massive)
            await bot.send_message(
                message.from_user.id, constants.TEMPLATE_MEDIA.format(
                    product.name, product.correct_structure, product.footage, product.correct_price
                ), reply_markup=order_keyboard(str(product.id))
            )
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def add_cart_handler(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает добавление товара в корзину, входит в машину состояний
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        await FSMProduct.color_number.set()
        async with state.proxy() as data:
            price = Product.get(Product.id == int(call.data))
            data['price'] = price.price
            data['product_id'] = call.data
        await bot.send_message(call.from_user.id, constants.COLOR_NUMBER)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def color_number_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние color_number, сохраняет выбранный пользователем номер цвета
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if message.text.isdigit():
            async with state.proxy() as data:
                color_numbers = ColorNumber.select().where(ColorNumber.product == data['product_id'])
                flag = False
                for color_number in color_numbers:
                    if color_number.color_number == int(message.text):
                        data['color_number'] = color_number.id
                        flag = True
                        break
                if flag:
                    await FSMProduct.next()
                    await bot.send_message(message.from_user.id, constants.QUANTITY, reply_markup=quantity_keyboard())
                else:
                    await bot.send_message(message.from_user.id, constants.INCORRECT_COLOR_NUMBER)
                    await bot.send_message(message.from_user.id, constants.COLOR_NUMBER)
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_SECOND_NUMBER)
            await bot.send_message(message.from_user.id, constants.COLOR_NUMBER)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def quantity_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние quantity, сохраняет данные в БД и закрывает машину состояний.
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            CartUser(user_id=call.from_user.id, product=int(data['product_id']),
                     color_number=data['color_number'], quantity=call.data.split()[0], price=data['price']).save()
        await state.finish()
        await bot.send_message(call.from_user.id, constants.ADD_CART)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def my_cart_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает кнопку MY_SHOPPING_CART и выводит список товаров в корзине.
    :param message: Message
    :return: None
    """
    try:
        cart_users = CartUser.select().where(CartUser.user_id == message.from_user.id)
        if cart_users:
            for cart_user in cart_users:
                await bot.send_photo(
                    message.from_user.id,
                    photo=open('../pre_order/media/' + cart_user.color_number.image_id, 'rb'),
                    caption=constants.CART_TEMPLATE.format(
                        cart_user.product.name, cart_user.product.correct_structure,
                        cart_user.product.footage, cart_user.product.correct_price, cart_user.quantity
                    ),
                    reply_markup=delete_keyboard(str(cart_user.id))
                )
        else:
            await bot.send_message(message.from_user.id, constants.EMPTY_CART)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def delete_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает кнопку удалить. Удаляет товар из корзины.
    :param call: CallbackQuery
    :return: None
    """
    try:
        CartUser.delete_by_id(int(call.data))
        await bot.edit_message_caption(
            chat_id=call.from_user.id, message_id=call.message.message_id, caption=constants.DELETE
        )
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def my_pre_order_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает кнопку MY_PRE_ORDER и выводит список оформленнных заявок.
    :param message: Message
    :return: None
    """
    try:
        requests_user = Request.select().where(Request.user_id == message.from_user.id)
        if requests_user:
            for request in requests_user:
                await bot.send_photo(
                    message.from_user.id, open('../pre_order/media/' + request.color_number.image_id, 'rb'),
                    caption=constants.MY_PRE_ORDER.format(
                        request.product.name, request.product.correct_structure,
                        request.product.footage, request.product.correct_price,
                        request.quantity, request.status
                    )
                )
        else:
            await bot.send_message(message.from_user.id, constants.EMPTY_REQUEST)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def place_a_pre_order_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает кнопку PLACE_A_PRE_ORDER. Входит в машину состояния.
    :param message: Message
    :return: None
    """
    try:
        if PreOrder.get(PreOrder.status == 'Открыт'):
            cart_users = CartUser.select().where(CartUser.user_id == message.from_user.id)
            if cart_users:
                await FSMOrder.full_name.set()
                await bot.send_message(message.from_user.id, constants.FULL_NAME)
            else:
                await bot.send_message(message.from_user.id, constants.EMPTY_CART)
        else:
            await bot.send_message(message.from_user.id, constants.STATUS_CLOSE)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def full_name_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние full_name, сохраняет ФИО пользователя.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if len(message.text.split()) == 3:
            async with state.proxy() as data:
                data['full_name'] = message.text
            await FSMOrder.next()
            await bot.send_message(message.from_user.id, constants.PHONE)
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_NAME)
            await bot.send_message(message.from_user.id, constants.FULL_NAME)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def phone_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние phone, сохраняет номер телефона пользователя.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        pattern = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
        if message.text.startswith('+7') and [message.text[2:]] == re.findall(pattern, message.text[2:]) and \
                len(message.text) >= 12 or message.text.startswith('8') and [message.text[1:]] == \
                re.findall(pattern, message.text[1:]) and len(message.text) >= 11 or [message.text] == \
                re.findall(pattern, message.text) and len(message.text) >= 10:
            async with state.proxy() as data:
                data['phone'] = message.text
            await FSMOrder.next()
            await bot.send_message(message.from_user.id, constants.ADDRESS)
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_PHONE)
            await bot.send_message(message.from_user.id, constants.PHONE)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def address_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние address, сохраняет адрес пользователя.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            data['address'] = message.text
        await FSMOrder.next()
        await bot.send_message(message.from_user.id, constants.COMMENT)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def comment_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние comment, сохраняет данные в БД.
    Отправляет поставщику данные о заявке и закрывает состояние.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            carts_user = CartUser.select().where(CartUser.user_id == message.from_user.id)
            pre_order = PreOrder.select(PreOrder.id).where(PreOrder.status == 'Открыт')
            for cart_user in carts_user:
                created_at = datetime.today()
                Request(
                    pre_order=pre_order, product=cart_user.product, color_number=cart_user.color_number,
                    quantity=cart_user.quantity, full_name=data['full_name'], phone=data['phone'],
                    address=data['address'], comment=message.text, user_id=message.from_user.id,
                    created_at=created_at, price=cart_user.price
                ).save()
                request_id = Request.get(
                    Request.created_at == created_at, Request.user_id == message.from_user.id,
                    Request.product == cart_user.product, Request.color_number == cart_user.color_number
                ).id
                cart_user.delete_instance()
                provider = Profile.get(Profile.role == 'поставщик')
                if cart_user.quantity == 'Целая':
                    await bot.send_photo(
                        provider.user_id, photo=open('../pre_order/media/' + cart_user.color_number.image_id, 'rb'),
                        caption=constants.CART_TEMPLATE_PR.format(
                            cart_user.product.name, cart_user.product.correct_structure,
                            cart_user.product.footage, cart_user.product.price, cart_user.quantity
                        ),
                        reply_markup=confirm_keyboard(str(request_id))
                    )
            await bot.send_message(message.from_user.id, constants.REQUEST_COMPLETE)
            await bot.send_message(message.from_user.id, constants.OPEN_KEYBOARD)
        await state.finish()
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
        elif message.text == key_text.PRODUCT:
            await product_handler(message)
        elif message.text == key_text.MY_PRE_ORDER:
            await my_pre_order_handler(message)
        elif message.text == key_text.MY_SHOPPING_CART:
            await my_cart_handler(message)
        elif message.text == key_text.PLACE_A_PRE_ORDER:
            await place_a_pre_order_handler(message)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_user_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирующая все хэндлеры файла
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(product_handler, lambda message: message.text == key_text.PRODUCT, state=None)
    dp.register_message_handler(my_cart_handler, lambda message: message.text == key_text.MY_SHOPPING_CART, state=None)
    dp.register_message_handler(my_pre_order_handler, lambda message: message.text == key_text.MY_PRE_ORDER, state=None)
    dp.register_message_handler(
        place_a_pre_order_handler, lambda message: message.text == key_text.PLACE_A_PRE_ORDER, state=None
    )
    dp.register_callback_query_handler(
        add_cart_handler, lambda call: call.data in [str(pk.id) for pk in Product.select()], state=None
    )
    dp.register_message_handler(cancel_state, lambda message: message.text in [
        '/start', '/help', key_text.PRODUCT, key_text.MY_PRE_ORDER,
        key_text.MY_SHOPPING_CART, key_text.PLACE_A_PRE_ORDER
    ], state='*')
    dp.register_message_handler(color_number_state, content_types=['text'], state=FSMProduct.color_number)
    dp.register_callback_query_handler(quantity_state, state=FSMProduct.quantity)
    dp.register_callback_query_handler(
        delete_handler, lambda call: call.data in [str(pk.id) for pk in CartUser.select()], state=None
    )
    dp.register_message_handler(full_name_state, content_types=['text'], state=FSMOrder.full_name)
    dp.register_message_handler(phone_state, content_types=['text'], state=FSMOrder.phone)
    dp.register_message_handler(address_state, content_types=['text'], state=FSMOrder.address)
    dp.register_message_handler(comment_state, content_types=['text'], state=FSMOrder.comment)
