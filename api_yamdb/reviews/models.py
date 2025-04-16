"""Модуль моделей проекта."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Genre(models.Model):
    """Модель Жанров произведений."""
    name = models.CharField('Название жанра произведения', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель Категорий произведений."""
    name = models.CharField('Название категории произведения', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    """Модель Произведений."""
    name = models.CharField('Название произведения', max_length=200)
    year = models.IntegerField('Год выпуска', )
    rating = models.IntegerField('Рейтинг на основе отзывов', default=None)
    description = models.TextField('Описание произведения', )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        blank=True,
        null=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов',
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категории',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )

    def __str__(self):
        return self.name
