"""Widoki (warstwa Controller) domeny finansowej.

Widoki sa cienkie: walidacje robi serializer (DTO), a operacje zapisu
deleguja do warstwy services. Odczyt korzysta z warstwy selectors.
"""
from rest_framework import viewsets

from . import selectors, services
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """Pelny CRUD dla transakcji (list/create/retrieve/update/destroy).

    Etap 4: chroniony przez JWT (domyslne IsAuthenticated z settings).
    Kazdy uzytkownik widzi i modyfikuje wylacznie wlasne transakcje.
    """

    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        return selectors.transaction_list(user=user)

    def perform_create(self, serializer) -> None:
        user = getattr(self.request, "user", None)
        instance = services.create_transaction(
            user=user, **serializer.validated_data
        )
        serializer.instance = instance

    def perform_update(self, serializer) -> None:
        instance = services.update_transaction(
            transaction=serializer.instance, **serializer.validated_data
        )
        serializer.instance = instance
