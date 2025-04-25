from datetime import date

from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError('Username "me" is not allowed.')


def validate_year(self, value):
    if value > date.today().year:
        raise ValidationError(
            'Год произведения не может быть в будущем.'
        )
    return value
