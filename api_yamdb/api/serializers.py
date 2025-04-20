"""Модуль сериализаторов проекта."""
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum

from rest_framework import serializers

from reviews.models import Genre, Category, Title

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

        if user_with_email and user_with_email.username != username:
            raise serializers.ValidationError(
                'Данный email уже используется другим пользователем.'
            )

        if user_with_username and user_with_username.email != email:
            raise serializers.ValidationError(
                'Email не соответствует данным пользователя.',
            )

        return data


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для получения JWT token."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """
        Проверяет существует ли пользователь с именем username и кодом
        подтверждения confirmation_code.
        """
        username = data.get('username')
        code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден.')

        if user.confirmation_code != code:
            raise serializers.ValidationError('Неверный код подтверждения.')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор модели Жанров произведений."""
    titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Genre
        fields = ('name', 'slug', 'titles')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор модели Категорий произведений."""
    titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('name', 'slug', 'titles')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор модели Произведений."""
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        depth = 1

    def validate_year(self, value):
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError('Год произведения не может быть в будущем.')
        return value

    # def create(self, validated_data):
    #     if ('genre' or 'category') not in self.initial_data:
    #         title = Title.objects.create(**validated_data)
    #         return title

    def get_rating(self, obj):
        sum = obj.reviews.aggregate(Sum('score'))['score__sum']
        if sum:
            return sum / obj.reviews.count()
        return 0
