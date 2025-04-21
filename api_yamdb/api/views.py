"""Модуль вьюсетов."""
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, status, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Genre, Category, Title
from api.serializers import (
  SignupSerializer, TokenObtainSerializer, UserSerializer,
    GenreSerializer, CategorySerializer, TitleSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAdmin
from .utils import send_confirmation_email


User = get_user_model()


class SignupView(APIView):
    """
    Класс обрабатывает регистрацию пользователя и отправляет код подтверждения
    на указанный email.
    """
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
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Произведений."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
