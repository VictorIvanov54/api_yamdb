"""Модуль вьюсетов."""
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from reviews.models import Genre, Category, Title, Comment, Review
from api.serializers import (
    SignupSerializer, TokenObtainSerializer, UserSerializer,
    GenreSerializer, CategorySerializer,  # TitleSerializer,
    TitleReadSerializer, TitleWriteSerializer,
    ReviewSerializer, CommentSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdmin, IsAuthorOrModeratorOrAdmin
from .utils import send_confirmation_email

User = get_user_model()


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


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    # pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    http_method_names = ['get', 'post', 'delete']   # !!!! Добавила, чтобы описать какие методы разрешены

    def retrieve(self, request, *args, **kwargs):   # !!! Добавила, чтобы не разрешать метод GET для детализации жанра
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    # pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    http_method_names = ['get', 'post', 'delete']   # !!!! Добавила, чтобы описать какие методы разрешены

    def retrieve(self, request, *args, **kwargs):   # !!! Добавила, чтобы не разрешать метод GET для детализации категории
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Произведений."""
    queryset = Title.objects.all()
    # serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    # pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year',)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        if title_id is not None:
            get_object_or_404(Title, pk=title_id)
            return Review.objects.filter(title__id=title_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)

        if Review.objects.filter(author=self.request.user, title=title).exists():
            raise ValidationError("Вы уже оставили отзыв на это произведение.")

        serializer.save(author=self.request.user, title=title)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            # Используем str(e) для получения сообщения об ошибке
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrModeratorOrAdmin]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        if review_id is not None:
            get_object_or_404(Review, pk=review_id)
            return Comment.objects.filter(review__id=review_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
