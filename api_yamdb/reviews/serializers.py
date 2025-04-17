from rest_framework import serializers

from .models import Review, Comment

from api.serializers import UserSerializer, TitleSerializer


class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    title = TitleSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'score', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date', 'title')


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')
