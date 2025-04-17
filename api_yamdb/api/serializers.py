from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
        fields = super().get_fields()
        request = self.context.get('request')

        if request and not request.user.is_admin:
            fields['role'].read_only = True
        return fields

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено.')
        return value


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Имя "me" запрещено.')
        return value


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
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
