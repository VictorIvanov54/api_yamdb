import secrets

from django.core.mail import send_mail
from django.conf import settings


def generate_confirmation_code():
    """Функция генерирует 6-значный код подтверждения."""
    return ''.join(secrets.choice('0123456789') for _ in range(6))


def send_confirmation_email(user):
    """Отправляет письмо с кодом подтверждения на email пользователя."""
    subject = 'Код подтверждения регистрации'
    message = (
        f'Здравствуйте, {user.username},\n\nВаш код: {user.confirmation_code}')
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(
        subject, message, from_email, recipient_list, fail_silently=False
    )
