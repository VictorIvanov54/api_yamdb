from rest_framework import serializers
from reviews.models import Review, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


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
