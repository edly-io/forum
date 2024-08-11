"""
URLs for forum.
"""

from django.urls import include, path

from forum.views.flags import CommentFlagAPIView, ThreadFlagAPIView
from forum.views.proxy import ForumProxyAPIView

api_patterns = [
    # Proxy view for various API endpoints
    path("comments/<str:comment_id>/abuse_<str:action>", CommentFlagAPIView.as_view(), name="comment-flags-api"),
    path("threads/<str:thread_id>/abuse_<str:action>", ThreadFlagAPIView.as_view(), name="thread-flags-api"),
    path("<path:suffix>", ForumProxyAPIView.as_view(), name="forum_proxy"),
]

urlpatterns = [
    path("api/v2/", include(api_patterns)),
]
