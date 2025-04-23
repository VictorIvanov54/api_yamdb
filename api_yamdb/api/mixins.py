"""Модуль Миксинов"""
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers

from reviews.models import User


class ListCreateDeleteViewSet(
    ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet,
):
    pass


class UserValidationMixin:
    """Миксин с валидацией имени пользователя и email."""

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Это имя пользователя уже используется.'
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Этот email уже используется.')
        return value
