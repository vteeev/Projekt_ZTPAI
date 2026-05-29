"""Routing aplikacji finance."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BudgetViewSet,
    ByCategoryStatsView,
    CategoryViewSet,
    MonthlyStatsView,
    ReportViewSet,
    SummaryStatsView,
    TransactionViewSet,
)

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("stats/summary/", SummaryStatsView.as_view(), name="stats-summary"),
    path("stats/by-category/", ByCategoryStatsView.as_view(), name="stats-by-category"),
    path("stats/monthly/", MonthlyStatsView.as_view(), name="stats-monthly"),
    *router.urls,
]
