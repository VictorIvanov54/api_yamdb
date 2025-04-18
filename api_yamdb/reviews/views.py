from rest_framework import viewsets, permissions, exceptions
from .models import Review, Comment
from api.models import Title
from .serializers import ReviewSerializer, CommentSerializer
from api.permissions import IsAuthorOrModeratorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id:
            try:
                Title.objects.get(pk=title_id)
            except Title.DoesNotExist:
                raise exceptions.NotFound('Произведение не найдено.')
            return Review.objects.filter(title__id=title_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = Title.objects.get(pk=title_id)
        serializer.save(author=self.request.user, title=title)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        if review_id:
            return Comment.objects.filter(review__id=review_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = Review.objects.get(pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
