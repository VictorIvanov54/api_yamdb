"""Модуль вьюсетов."""
from django.db.models import Avg
from django.forms import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from api.filters import TitleFilter
from api.mixins import ListCreateDeleteViewSet
from api.permissions import (
    IsAdminOrReadOnly, IsAdmin, IsAuthorOrModeratorOrAdmin
)
from api.serializers import (
    SignupSerializer, TokenObtainSerializer, UserSerializer,
    GenreSerializer, CategorySerializer,
    TitleReadSerializer, TitleWriteSerializer,
    ReviewSerializer, CommentSerializer
)
from api.utils import send_confirmation_email
from reviews.models import User, Genre, Category, Title, Comment, Review


class SignupView(APIView):
    """
    Класс обрабатывает регистрацию пользователя и отправляет код подтверждения
    на указанный email.
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']

            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )

            user.set_confirmation_code()
            send_confirmation_email(user)

            return Response({'email': email, 'username': username},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainView(APIView):
    """
    Класс обрабатывает JWT access tokens для пользователей. Пользователи
    должны предоставить зарегистрированный username и confirmation_code.
    """

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response('username - необходимое поле.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return Response('Пользователь не найден.',
                            status=status.HTTP_404_NOT_FOUND)

        data = TokenObtainSerializer(data=request.data)
        if not data.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления объектами пользователя. Ендпоинты:
    - /users/ [GET, POST]
    - /users/{username}/ [GET, PATCH, DELETE]
    - /users/me/ [GET, PATCH]
    """
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        """
        Предоставляет ендпоинт users/me/.
        Аутентифицированный пользователь может изменять и просматривать
        только свои данные.
        """
        if request.method == 'GET':
            user = self.get_serializer(request.user)
            return Response(user.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(ListCreateDeleteViewSet):
    """Вьюсет модели Жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', 'slug')


class CategoryViewSet(ListCreateDeleteViewSet):
    """Вьюсет модели Категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Произведений."""
    queryset = (
        Title.objects.all()
        .annotate(rating=Avg('reviews__score'))
        .order_by('name')
    )
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ['get', 'post', 'delete', "patch"]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        """Возвращает объект Title по ID из URL или вызывает 404."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = self.get_title()
        if Review.objects.filter(author=self.request.user,
                                 title=title).exists():
            raise ValidationError("Вы уже оставили отзыв на это произведение.")
        serializer.save(author=self.request.user, title=title)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            # Используем str(e) для получения сообщения об ошибке
            return Response({"detail": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Комментариев."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        """Возвращает title_id из URL параметров или вызывает исключение."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
