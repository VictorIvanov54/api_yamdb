"""Модуль моделей проекта."""
import secrets
import string

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.validators import validate_username, validate_year


class User(AbstractUser):
    """Кастомная модель пользователя."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]

    role_max_length = max(len(role) for role, _ in ROLE_CHOICES)

    email = models.EmailField(
        max_length=settings.MAX_LENGTH,
        unique=True,
        verbose_name='Email',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Biography',
    )
    role = models.CharField(
        max_length=role_max_length,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Role',
    )
    confirmation_code = models.CharField(
        max_length=settings.MAX_LENGTH_CODE,
        blank=True,
        verbose_name='Confirmation code'
    )

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def clean(self):
        super().clean()
        validate_username(self.username)

    def set_confirmation_code(self, length=6):
        self.confirmation_code = ''.join(
            secrets.choice(string.digits) for _ in range(length)
        )
        self.save()


class Genre(models.Model):
    """Модель Жанров произведений."""
    name = models.CharField(
        'Название жанра произведения', max_length=settings.MAX_LENGTH_NAME
    )
    slug = models.SlugField(max_length=settings.MAX_LENGTH_SLUG, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель Категорий произведений."""
    name = models.CharField(
        'Название категории произведения', max_length=settings.MAX_LENGTH_NAME
    )
    slug = models.SlugField(max_length=settings.MAX_LENGTH_SLUG, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель Произведений."""
    name = models.CharField('Название произведения',
                            max_length=settings.MAX_LENGTH_NAME)
    year = models.SmallIntegerField('Год выпуска', )
    description = models.TextField('Описание произведения', blank=True)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов',
        related_name='titles',
        verbose_name='Жанры',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категории',
    )

    class Meta:
        ordering = ('name',)

    def clean(self):
        super().clean()
        validate_year(self.year)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка', choices=[(i, str(i)) for i in range(1, 11)]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('author', 'title')

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    """Модель комментариев."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:settings.MAX_LENGTH_BEGINNING_TEXT]
