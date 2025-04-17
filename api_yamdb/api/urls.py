from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import GenreViewSet, CategoryViewSet, TitleViewSet


router = DefaultRouter()
router.register('genre', GenreViewSet, basename='genre')
router.register('category', CategoryViewSet, basename='category')
router.register('title', TitleViewSet, basename='title')

urlpatterns = [
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
    # path('', include('djoser.urls.jwt')),
]
