from django.urls import path
from .views import SignupView
from .views import TokenObtainView

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
]
