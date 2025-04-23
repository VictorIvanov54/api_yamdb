"""Модуль Миксинов"""
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, DestroyModelMixin,
)
from rest_framework.viewsets import GenericViewSet


class ListCreateDeleteViewSet(
    ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet,
):
    pass
