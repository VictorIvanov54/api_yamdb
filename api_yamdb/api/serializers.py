"""Модуль сериализаторов проекта."""
from django.conf import settings

from rest_framework import serializers

from reviews.models import User, Genre, Category, Title, Review, Comment
from .mixins import UserValidationMixin


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'score', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date', 'title')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date', 'review')

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                'Комментарий не может быть пустым.')
        return value


class UserSerializer(UserValidationMixin, serializers.ModelSerializer):
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

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор модели Категорий произведений."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        depth = 1
