"""Jednolita obsluga bledow dla API (kryterium 4.0)."""
from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context) -> Response | None:
    """Opakowuje odpowiedzi bledow w spojny format JSON.

    Format:
    {
        "error": {
            "status_code": 400,
            "type": "ValidationError",
            "detail": {...}
        }
    }
    """
    response = exception_handler(exc, context)
    if response is None:
        return None

    response.data = {
        "error": {
            "status_code": response.status_code,
            "type": exc.__class__.__name__,
            "detail": response.data,
        }
    }
    return response
