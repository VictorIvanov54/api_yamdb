from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SignupView, TokenObtainView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('', include(router.urls)),
]
