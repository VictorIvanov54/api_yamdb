"""Модуль сериализаторов проекта."""
from datetime import date
from django.db.models import Sum
from rest_framework import serializers

from reviews.models import Genre, Category, Title


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
