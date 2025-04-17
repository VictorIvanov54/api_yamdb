from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
        read_only_fields = ('role',)

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
            raise serializers.ValidationError({'username': 'User not found'})

        if user.confirmation_code != code:
            raise serializers.ValidationError({'confirmation_code': 'Invalid code'})

        data['user'] = user
        return data
