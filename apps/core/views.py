"""Endpointy infrastrukturalne (health-check)."""
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Sprawdza, czy aplikacja dziala i ma polaczenie z baza danych."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        db_ok = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            db_ok = False

        return Response(
            {
                "status": "ok" if db_ok else "degraded",
                "database": "connected" if db_ok else "unavailable",
            }
        )
