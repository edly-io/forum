"""
URLs for forum.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter
from forum.api.v2.threds import CommentThreadViewSet
from forum.views import ForumProxyAPIView

router = DefaultRouter()
router.register(r'comment_threads', CommentThreadViewSet,  basename='comment_threds')

urlpatterns = [
    path("/forum_proxy<path:suffix>/", ForumProxyAPIView.as_view(), name="forum_proxy"),
    path("/api/v2/", include(router.urls))
]
