"""Модуль моделей проекта."""
import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


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
        max_length=settings.MAX_LENGTH_ROLE,
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
        if self.username.lower() == 'me':
            raise ValidationError('Username "me" не разрешено.')

    def set_confirmation_code(self):
        self.confirmation_code = ''.join(
            secrets.choice('0123456789') for _ in range(6)
        )
        self.save()
        
        
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


class Title(models.Model):
    """Модель Произведений."""
    name = models.CharField('Название произведения', max_length=256)
    year = models.PositiveIntegerField('Год выпуска', )
    rating = models.IntegerField('Рейтинг на основе отзывов', default=None)
    description = models.TextField('Описание произведения', blank=True)
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        blank=True,
        null=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов',
        # on_delete=models.SET_NULL,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категории',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        'api.Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    score = models.IntegerField('Оценка',
                                choices=[(i, str(i)) for i in range(1, 11)])
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
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
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:50]
