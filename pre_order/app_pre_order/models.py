from django.db import models


class Replace(models.Model):
    regular = models.CharField(max_length=200, verbose_name='Реплейсы')
    text = models.TextField(verbose_name='Текст')

    def __str__(self):
        return f"{self.regular}"

    class Meta:
        verbose_name = 'Реплейс'
        verbose_name_plural = 'Реплейсы'
        db_table = 'replace'


class Product(models.Model):
    name = models.CharField(max_length=700, blank=True, null=True, verbose_name='Наименование')
    article = models.CharField(max_length=700, blank=True, null=True, verbose_name='Артикул')
    structure = models.CharField(max_length=700, blank=True, null=True, verbose_name='Состав')
    correct_structure = models.CharField(max_length=700, blank=True, null=True, verbose_name='Состав скорректированный')
    footage = models.CharField(max_length=700, blank=True, null=True, verbose_name='Метраж')
    price = models.FloatField(blank=True, null=True, verbose_name='Цена')
    correct_price = models.FloatField(blank=True, null=True, verbose_name='Цена скорректированная')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'product'


class ColorNumber(models.Model):
    product = models.ForeignKey(
        Product, related_name='color_number', null=True, on_delete=models.SET_NULL, verbose_name='id товара'
    )
    color_number = models.BigIntegerField(verbose_name='Номер цвета')
    image_id = models.ImageField(upload_to='pillow/', blank=True, null=True, verbose_name='Изображение ID')

    def __str__(self):
        return f"{self.color_number}"

    class Meta:
        verbose_name = 'Номер цвета'
        verbose_name_plural = 'Номера цветов'
        db_table = 'color_number'


class PreOrder(models.Model):
    PRE_ORDER_CHOICES = [
        ('Открыт', 'Открыт'),
        ('Закрыт', 'Закрыт'),
    ]
    name = models.CharField(max_length=700, blank=True, null=True, verbose_name='Наименование')
    status = models.CharField(max_length=20, choices=PRE_ORDER_CHOICES, default='Закрыт', verbose_name='Статус')
    opening_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата открытия')
    closing_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Предзаказ'
        verbose_name_plural = 'Предзаказы'
        db_table = 'pre_order'


class AdminPanel(models.Model):
    key = models.CharField(max_length=50, verbose_name='Ключ')
    value = models.FloatField(verbose_name='Значение')

    def __str__(self):
        return f"{self.key}"

    class Meta:
        verbose_name = 'Админ-панель'
        verbose_name_plural = 'Админ-панель'
        db_table = 'admin_panel'


class Request(models.Model):
    REQUEST_STATUS = [
        ('Новая', 'Новая'),
        ('Не подтверждена', 'Не подтверждена'),
        ('Подтверждена', 'Подтверждена'),
    ]

    QUANTITY = [
        ('Целая', 'Целая'),
        ('Половина', 'Половина'),
    ]

    pre_order = models.ForeignKey(
        PreOrder, related_name='user_request', null=True, on_delete=models.SET_NULL, verbose_name='Предзаказ'
    )
    product = models.ForeignKey(
        Product, related_name='user_request', null=True, on_delete=models.SET_NULL, verbose_name='Товар'
    )
    color_number = models.ForeignKey(
        ColorNumber, related_name='user_request', null=True, on_delete=models.SET_NULL, verbose_name='Номер цвета'
    )
    quantity = models.CharField(max_length=20, choices=QUANTITY, verbose_name='Количество')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    phone = models.CharField(max_length=100, verbose_name='Телефон')
    address = models.CharField(max_length=500, verbose_name='Адрес')
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='Новая', verbose_name='Статус')
    user_id = models.BigIntegerField(blank=True, null=True, verbose_name='id_пользователя')
    price = models.FloatField(blank=True, null=True, verbose_name='Цена')

    def __str__(self):
        return f"{self.product}"

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        db_table = 'request'


class Profile(models.Model):
    PROFILE_CHOICES = [('администратор', 'администратор'), ('поставщик', 'поставщик')]

    user_id = models.BigIntegerField(verbose_name='id_пользователя')
    role = models.CharField(max_length=20, choices=PROFILE_CHOICES, verbose_name='Роль')

    def __str__(self):
        return f"{self.user_id}"

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        db_table = 'profile'


class CartUser(models.Model):
    QUANTITY = [
        ('Целая', 'Целая'),
        ('Половина', 'Половина'),
    ]
    user_id = models.BigIntegerField(verbose_name='id_пользователя')
    product = models.ForeignKey(
        Product, related_name='cart_user', null=True, on_delete=models.SET_NULL, verbose_name='Товар'
    )
    color_number = models.ForeignKey(
        ColorNumber, related_name='cart_user', null=True, on_delete=models.SET_NULL, verbose_name='Номер цвета'
    )
    quantity = models.CharField(max_length=20, choices=QUANTITY, verbose_name='Количество')
    price = models.FloatField(blank=True, null=True, verbose_name='Цена')

    def __str__(self):
        return f"{self.product}"

    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзина пользователя'
        db_table = 'cart_user'
