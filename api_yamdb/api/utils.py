from django.core.mail import send_mail
from django.conf import settings


def send_confirmation_email(user):
    """Отправляет письмо с кодом подтверждения на email пользователя."""
    subject = 'Код подтверждения регистрации'
    message = (
        f"""Здравствуйте, {user.username},\n
        Ваш код подтвержения регистрации: {user.confirmation_code}""")
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
