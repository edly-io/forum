"""
URLs for forum.
"""

from django.urls import path

from forum.views.flags import CommentFlagAPIView, ThreadFlagAPIView
from forum.views.proxy import ForumProxyAPIView

urlpatterns = [
    path('api/v2/comments/<str:comment_id>/abuse_<str:action>', CommentFlagAPIView.as_view(), name="comment-flags-api"),
    path('api/v2/threads/<str:thread_id>/abuse_<str:action>', ThreadFlagAPIView.as_view(), name="thread-flags-api"),
    path("forum_proxy<path:suffix>", ForumProxyAPIView.as_view(), name="forum_proxy"),
]
