"""Модуль вьюсетов."""
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from reviews.models import Genre, Category, Title
from api.serializers import (
    GenreSerializer, CategorySerializer, TitleSerializer,
    # UserSerializer, 
)
from .permissions import IsAdminOrReadOnly


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """Вьюсет модели Пользователей."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Произведений."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
