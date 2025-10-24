from django.contrib import admin
from .models import *
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Product._meta.fields]
@admin.register(SavingsEntry)
class SavingsEntryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SavingsEntry._meta.fields]
