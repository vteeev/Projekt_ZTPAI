from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "amount", "category", "date", "user")
    list_filter = ("type", "date")
    search_fields = ("category", "description")
    date_hierarchy = "date"
