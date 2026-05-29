from django.contrib import admin

from .models import Budget, Category, Report, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "color", "user")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "amount", "category", "date", "user")
    list_filter = ("type", "date")
    search_fields = ("description",)
    date_hierarchy = "date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "month", "year", "amount", "user")
    list_filter = ("year", "month")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "status", "month", "year", "user", "created_at")
    list_filter = ("type", "status")
