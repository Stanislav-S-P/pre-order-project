"""
Файл - содержит хэндлер для отлова сообщений вне сценария
"""
import os
import re
from typing import List
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from loader import bot, logger
from settings import constants
from database.models import *
from PIL import Image, ImageDraw, ImageFont


def text_logic(string_list: List, name_i: int, str_i: int, foot_i: int, pri_i: int) -> Tuple:
    """
    Функция - обрабатывает полученный текст и подготавливает его к сохранению в БД.
    :param string_list: List
    :param name_i: int
    :param str_i: int
    :param foot_i: int
    :param pri_i: int
    :return: Tuple
    """
    try:
        for index, elem in enumerate(string_list):
            if index == name_i:
                name = elem
            elif index == str_i:
                structure = elem
                structure_list = re.findall(r'[a-zA-Z]+', elem)
                for i in structure_list:
                    value = Replace.get_or_none(Replace.regular == i.upper())
                    if value is not None:
                        elem = re.sub(rf"{i}", value.text, elem)
                correct_structure = elem
            elif index == foot_i:
                footage = elem
            elif index == pri_i:
                price_euro = re.findall(r'\d+', elem)[0]
                course = AdminPanel.get(AdminPanel.key == 'Курс').value
                margin = AdminPanel.get(AdminPanel.key == 'Маржа').value
                price = round(float(price_euro) * course, 2)
                correct_price = round(price / 100 * margin + price, 2)
        return name, structure, correct_structure, footage, price_euro, correct_price
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def echo_text_handler(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - оповещает о некорректной команде (Эхо), или же сохраняет товар в БД.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        with db:
            profile = Profile.get(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    article = int(message.date.timestamp())
                    string_list = message.text.split('\n')
                    if len(string_list) == 4:
                        name, structure, correct_structure, footage, price, correct_price = text_logic(
                            string_list, 0, 1, 2, 3
                        )
                    elif len(string_list) == 5:
                        name, structure, correct_structure, footage, price, correct_price = text_logic(
                            string_list, 1, 2, 3, 4
                        )
                    product = Product.get_or_none(Product.article == int(message.date.timestamp()))
                    if product:
                        Product.update(
                            name=name, structure=structure, correct_structure=correct_structure,
                            footage=footage, price=price, correct_price=correct_price
                        ).where(Product.article == article).execute()
                    else:
                        Product(
                            article=article, name=name, structure=structure, correct_structure=correct_structure,
                            footage=footage, price=price, correct_price=correct_price
                        ).save()
                else:
                    await bot.send_message(message.from_user.id, constants.INCORRECT_INPUT)
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def echo_photo_handler(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - сохраняет фотографии с цветами товаров,
    предварительно нанеся на них артикул и номер цвета.
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        with db:
            profile = Profile.get(Profile.user_id == message.from_user.id)
            try:
                if profile.role == 'администратор':
                    product = Product.get_or_none(Product.article == int(message.date.timestamp()))
                    if not product:
                        Product(article=int(message.date.timestamp())).save()
                        product = Product.get(Product.article == int(message.date.timestamp()))
                    file_id = message.photo[len(message.photo) - 1].file_id
                    file_path = (await bot.get_file(file_id)).file_path
                    downloaded_file = await bot.download_file(file_path)
                    src = os.path.abspath(os.path.join('../pre_order/media/', file_path))
                    with open(src, 'wb') as new_file:
                        new_file.write(downloaded_file.read())
                    photo = Image.open('../pre_order/media/' + file_path)
                    drawing = ImageDraw.Draw(photo)
                    white = (255, 255, 255)
                    font = ImageFont.truetype('font/arial.ttf', 46)
                    color_number = ColorNumber.select().where(
                        ColorNumber.product == product.id
                    ).order_by(ColorNumber.color_number.desc())
                    if color_number:
                        for obj in color_number:
                            number = obj.color_number + 1
                            break
                    else:
                        number = 1
                    drawing.text((10, 10), f'Артикул: {str(int(message.date.timestamp()))}\nНомер цвета: {number}',
                                 fill=white, font=font)
                    file_name = re.findall(r'(?<=/)\w+[.]\w+', file_path)[0]
                    photo.save(f'../pre_order/media/pillow/{file_name}')
                    os.remove('../pre_order/media/' + file_path)
                    product_id = Product.get_or_none(Product.article == int(message.date.timestamp()))
                    if product_id:
                        ColorNumber(product=product_id.id, color_number=number, image_id=f'pillow/{file_name}').save()
            except AttributeError:
                pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_echo_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирует все хэндлеры файла
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(echo_text_handler, content_types=['text'])
    dp.register_message_handler(echo_photo_handler, content_types=['photo'])
