from rest_framework import viewsets, permissions
from rest_framework import exceptions  # Import exceptions

from django.shortcuts import get_object_or_404

from .models import Comment, Review, Title
from api.serializers import ReviewSerializer, CommentSerializer
from api.permissions import IsAuthorOrModeratorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = IsAuthorOrModeratorOrAdmin

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id is not None:
            # get_object_or_404 поднимает исключение, если объект не найден
            get_object_or_404(Title, pk=title_id)
            return Review.objects.filter(title__id=title_id)
        return Review.objects.all()  # Или return Review.objects.none()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = IsAuthorOrModeratorOrAdmin

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        if review_id is not None:
            # get_object_or_404 поднимает исключение, если объект не найден
            get_object_or_404(Review, pk=review_id)
            return Comment.objects.filter(review__id=review_id)
        return Comment.objects.all()  # Или return Comment.objects.none()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)
