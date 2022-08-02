"""
Файл с моделями базы данных
"""


from peewee import *
from settings.settings import DATABASE, USER, PASSWORD, HOST, PORT


db = PostgresqlDatabase(
    DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class Replace(BaseModel):
    regular = CharField(max_length=200)
    text = TextField()

    class Meta:
        db_table = 'replace'


class Product(BaseModel):
    name = CharField(max_length=700, null=True)
    article = CharField(max_length=700, null=True)
    structure = CharField(max_length=700, null=True)
    correct_structure = CharField(max_length=700, null=True)
    footage = CharField(max_length=700, null=True)
    price = FloatField(null=True)
    correct_price = FloatField(null=True)

    class Meta:
        db_table = 'product'


class ColorNumber(BaseModel):
    product = ForeignKeyField(Product, null=True, on_delete='SET_NULL')
    color_number = BigIntegerField()
    image_id = CharField(max_length=250, null=True)

    class Meta:
        db_table = 'color_number'


class PreOrder(BaseModel):
    name = CharField(max_length=700, null=True)
    status = CharField(max_length=20, default='Закрыт')
    opening_date = DateTimeField(null=True)
    closing_date = DateTimeField(null=True)

    class Meta:
        db_table = 'pre_order'


class AdminPanel(BaseModel):
    key = CharField(max_length=50)
    value = FloatField()

    class Meta:
        db_table = 'admin_panel'


class Request(BaseModel):
    pre_order = ForeignKeyField(PreOrder, null=True, on_delete='SET_NULL')
    product = ForeignKeyField(Product, null=True, on_delete='SET_NULL')
    color_number = ForeignKeyField(ColorNumber, null=True, on_delete='SET_NULL')
    quantity = CharField(max_length=20)
    full_name = CharField(max_length=150)
    phone = CharField(max_length=100)
    address = CharField(max_length=500)
    comment = TextField()
    created_at = DateTimeField()
    status = CharField(max_length=20, default='Новая')
    user_id = BigIntegerField()
    price = FloatField(null=True)

    class Meta:
        db_table = 'request'


class Profile(BaseModel):
    user_id = BigIntegerField()
    role = CharField(max_length=20)

    class Meta:
        db_table = 'profile'


class CartUser(BaseModel):
    user_id = BigIntegerField()
    product = ForeignKeyField(Product, null=True, on_delete='SET_NULL')
    color_number = ForeignKeyField(ColorNumber, null=True, on_delete='SET_NULL')
    quantity = CharField(max_length=20)
    price = FloatField(null=True)

    class Meta:
        db_table = 'cart_user'
