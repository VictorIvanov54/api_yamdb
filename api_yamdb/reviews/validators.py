from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError("Username 'me' is not allowed.")
