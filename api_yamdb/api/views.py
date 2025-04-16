from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer
# from .utils import send_confirmation_email
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']

            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )

            if not created and user.email != email:
                user.email = email
                user.save()

            # send confirmation code
            # confirmation_code = send_confirmation_email(user)

            return Response({'email': email, 'username': username}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
