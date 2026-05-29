"""Widoki (warstwa Controller) domeny finansowej."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """Pelny CRUD dla transakcji (list/create/retrieve/update/destroy).

    Etap 2: endpoint otwarty (AllowAny). W Etapie 4 zostanie objety JWT
    oraz izolacja danych per uzytkownik.
    """

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [AllowAny]
