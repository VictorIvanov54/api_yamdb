from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (SignupView, TokenObtainView, UserViewSet, 
                       GenreViewSet, CategoryViewSet, TitleViewSet
                      )

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('genres', GenreViewSet, basename='genres')
router.register('categories', CategoryViewSet, basename='categories')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('', include(router.urls)),
]
