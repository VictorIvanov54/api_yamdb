from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User. Для всех пользователей."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        allow_blank=False,
        max_length=settings.MAX_LENGTH_USERNAME
    )
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=settings.MAX_LENGTH
    )
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default=User.USER,
        required=False
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def get_fields(self):
        """
        Функция осуществляет контроль, чтобы поле 'role' мог изменять только
        пользователь с правами администратора.
        """
        fields = super().get_fields()
        request = self.context.get('request')

        if request and not request.user.is_admin:
            fields['role'].read_only = True
        return fields

    def validate_username(self, value):
        """Функция запрещает задавать имя 'me' в поле 'username'."""
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


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователей."""
    email = serializers.EmailField(max_length=settings.MAX_LENGTH)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=settings.MAX_LENGTH_USERNAME
    )

    def validate_username(self, value):
        """Функция запрещает задавать имя 'me' в поле 'username'."""
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено.')
        return value

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        user_with_email = User.objects.filter(email=email).first()
        user_with_username = User.objects.filter(username=username).first()

        # Проверка, принадлежит ли email другому пользователю
        if user_with_email and user_with_email.username != username:
            raise serializers.ValidationError({
                'email': 'Такой email уже используется другим пользователем.'
            })

        # Проверка соответствия username и email
        if user_with_username and user_with_username.email != email:
            raise serializers.ValidationError({
                'email': 'Email не соответствует данным пользователя.',
            })

        return data


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения JWT token."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """
        Проверяет существует ли пользователь с именем username и код
        подтверждения confirmation_code.
        """
        username = data.get('username')
        code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь не найден.'}
            )

        if user.confirmation_code != code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )

        data['user'] = user
        return data
