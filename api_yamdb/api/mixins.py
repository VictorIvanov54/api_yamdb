"""Модуль Миксинов"""

from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers, filters

from api.permissions import IsAdminOrReadOnly
from reviews.models import User


class ListCreateDeleteViewSet(
    ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', 'slug')


class UserValidationMixin:
    """Миксин с валидацией имени пользователя и email."""

    # def validate_username(self, value):
    #     if value.lower() == 'me':
    #         raise serializers.ValidationError('Имя "me" запрещено.')
    #     if User.objects.filter(username=value).exists():
    #         raise serializers.ValidationError(
    #             'Это имя пользователя уже используется.'
    #         )
    #     return value

    # def validate_email(self, value):
    #     if User.objects.filter(email=value).exists():
    #         raise serializers.ValidationError('Этот email уже используется.')
    #     return value

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено.')
        return value

    def validate(self, data):
        """Проверяет уникальность username/email, но позволяет повторение
        только если они принадлежат одному и тому же пользователю."""
        email = data.get('email')
        username = data.get('username')

        if email and username:
            user_with_email = User.objects.filter(email=email).first()
            user_with_username = User.objects.filter(username=username).first()

            if user_with_email and user_with_email.username != username:
                raise serializers.ValidationError(
                    'Данный email уже используется другим пользователем.'
                )

            if user_with_username and user_with_username.email != email:
                raise serializers.ValidationError(
                    'Email не соответствует данным пользователя.',
                )

        return data
