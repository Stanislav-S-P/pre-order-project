import requests
from admin_totals.admin import ModelAdminTotals
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'article', 'structure', 'correct_structure', 'footage', 'price', 'correct_price']
    list_display_links = [
        'id', 'name', 'article', 'structure', 'correct_structure', 'footage', 'price', 'correct_price'
    ]
    list_filter = ['structure']


class ReplaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'regular', 'text']
    list_display_links = ['id', 'regular', 'text']


class ColorNumberAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'color_number', 'image_id']
    list_display_links = ['id', 'product', 'color_number', 'image_id']


class PreOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'opening_date', 'closing_date']
    list_display_links = ['id', 'name', 'status', 'opening_date', 'closing_date']
    list_filter = ['status']


class AdminPanelAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'value']
    list_display_links = ['id', 'key', 'value']


class RequestAdmin(ModelAdminTotals):
    list_display = [
        'id', 'pre_order', 'product', 'color_number', 'quantity',
        'full_name', 'phone', 'address', 'comment', 'created_at', 'price', 'status'
    ]
    list_display_links = [
        'id', 'pre_order', 'product', 'color_number', 'quantity',
        'full_name', 'phone', 'address', 'comment', 'created_at', 'price', 'status'
    ]
    list_filter = ['status']
    list_totals = [('price', lambda field: Coalesce(Sum(field), 0, output_field=FloatField()))]
    actions = ['mark_as_no', 'mark_as_yes']

    def mark_as_no(self, request, queryset):
        for elem in queryset:
            elem.status = 'Не подтверждена'
            elem.save()
            text = f'Количество бобин: {elem.quantity} \n\nСтатус заявки изменен: {elem.status}'
            url = "https://api.telegram.org/bot<токен бота>/sendPhoto"
            photo = {'photo': open('media/' + str(elem.color_number.image_id), 'rb')}
            data = {'chat_id': elem.user_id, 'caption': text}
            requests.post(url, files=photo, data=data)

    def mark_as_yes(self, request, queryset):
        for elem in queryset:
            elem.status = 'Подтверждена'
            elem.save()
            text = f'Количество бобин: {elem.quantity} \n\nСтатус заявки изменен: {elem.status}'
            url = "https://api.telegram.org/bot<токен бота>/sendPhoto"
            photo = {'photo': open('media/' + str(elem.color_number.image_id), 'rb')}
            data = {'chat_id': elem.user_id, 'caption': text}
            requests.post(url, files=photo, data=data)

    mark_as_no.short_description = 'Перевести в статус Не подтвержден'
    mark_as_yes.short_description = 'Перевести в статус Подтвержден'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'role']
    list_display_links = ['user_id', 'role']


class CartUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'product', 'color_number', 'quantity']
    list_display_links = ['user_id', 'product', 'color_number', 'quantity']


admin.site.register(Product, ProductAdmin)
admin.site.register(Replace, ReplaceAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(AdminPanel, AdminPanelAdmin)
admin.site.register(PreOrder, PreOrderAdmin)
admin.site.register(ColorNumber, ColorNumberAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CartUser, CartUserAdmin)


admin.site.unregister(User)
admin.site.unregister(Group)


admin.site.site_title = 'Система предзаказа'
admin.site.site_header = 'Система предзаказа'
