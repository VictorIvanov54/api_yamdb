from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer
from utils import send_confirmation_email


User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user, created = User.objects.get_or_create(username=username, email=email)

        if created:
            user.set_confirmation_code()
            send_confirmation_email(user)

        # return Response({"message": "Signup successful. Please check your email for the confirmation code."}, status=status.HTTP_201_CREATED)
