"""
URLs for forum.
"""

from django.urls import path

from forum.views import ForumProxyAPIView

urlpatterns = [
    path("/forum_proxy<path:suffix>/", ForumProxyAPIView.as_view(), name="forum_proxy"),
]
