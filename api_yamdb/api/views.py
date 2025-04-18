from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAdmin
from .serializers import (SignupSerializer, TokenObtainSerializer,
                          UserSerializer)
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

            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            user.set_confirmation_code()
            if not created and user.email != email:
                user.email = email
                user.save()

            send_confirmation_email(user)

            return Response({'email': email, 'username': username},
                            status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainView(APIView):
    """
    Класс обрабатывает JWT access tokens для пользователей. Пользователи
    должны предоставить зарегистрированный username и confirmation_code.
    """
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({'token': str(refresh.access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления объектами пользователя. Ендпоинты:
    - /users/ [GET, POST]
    - /users/{username}/ [GET, PATCH, DELETE]
    - /users/me/ [GET, PATCH]
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
