"""Widoki kont uzytkownikow: rejestracja i profil."""
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Rejestracja nowego uzytkownika (otwarty endpoint)."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    """Zwraca dane zalogowanego uzytkownika (wymaga JWT)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)
