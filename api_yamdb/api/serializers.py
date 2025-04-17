"""Модуль сериализаторов проекта."""
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
    genre = GenreSerializer(many=True, required=False)
    category = CategorySerializer(many=True, required=False)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        depth = 1

    def create(self, validated_data):
        if ('genre' or 'category') not in self.initial_data:
            title = Title.objects.create(**validated_data)
            return title

    def get_rating(self, obj):
        total = obj.rating.aggregate(Sum('score'))['score__sum']  # Сумма всех оценок
        if total:
            return total / obj.rating.count()  # Деление суммы на количество
        return 0  # Возвращаем 0, если оценок нет
