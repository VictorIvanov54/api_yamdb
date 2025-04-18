from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, CommentViewSet

router = DefaultRouter()


router.register('titles/(?P<title_id>d+)/reviews', ReviewViewSet,
                basename='review')


comments_router = DefaultRouter()
comments_router.register('reviews/(?P<review_id>[^/.]+)/comments',
                         CommentViewSet, basename='review-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(comments_router.urls)),
]
