import secrets

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


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
        verbose_name='Confirmation Code'
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
