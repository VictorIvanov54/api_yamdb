# """Модуль вьюсетов."""
# from django.shortcuts import get_object_or_404

# from rest_framework import filters
# from rest_framework import viewsets
# from rest_framework.pagination import LimitOffsetPagination
# from rest_framework.permissions import IsAuthenticated

# from posts.models import Post, Group, Comment, User, Follow
# from api.serializers import (
#     PostSerializer, GroupSerializer, CommentSerializer,
#     UserSerializer, FollowSerializer
# )
# from .permissions import AuthorOrReadOnly, SafeMethods


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """Вьюсет модели Пользователей."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# class PostViewSet(viewsets.ModelViewSet):
#     """Вьюсет модели Постов."""
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = (AuthorOrReadOnly, )
#     pagination_class = LimitOffsetPagination

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)


# class GroupViewSet(viewsets.ReadOnlyModelViewSet):
#     """Вьюсет модели Групп."""
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#     permission_classes = (SafeMethods, )


# class CommentViewSet(viewsets.ModelViewSet):
#     """Вьюсет модели Комментариев."""
#     serializer_class = CommentSerializer
#     permission_classes = (AuthorOrReadOnly, )

#     def get_post_id(self):
#         return self.kwargs.get('post_id')

#     def get_queryset(self):
#         return Comment.objects.filter(post_id=self.get_post_id())

#     def perform_create(self, serializer):
#         post = get_object_or_404(Post, pk=self.get_post_id())
#         serializer.save(author=self.request.user, post=post)


# class FollowViewSet(viewsets.ModelViewSet):
#     """Вьюсет модели Подписок."""
#     serializer_class = FollowSerializer
#     permission_classes = (IsAuthenticated, )
#     filter_backends = (filters.SearchFilter, )
#     search_fields = ('following__username', )

#     def get_queryset(self):
#         return Follow.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
