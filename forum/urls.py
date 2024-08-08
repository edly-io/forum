"""
URLs for forum.
"""

from django.urls import path

from forum.views.proxy import ForumProxyAPIView
from forum.views.votes import CommentVoteView, ThreadVoteView

urlpatterns = [
    path("forum_proxy<path:suffix>/", ForumProxyAPIView.as_view(), name="forum_proxy"),
    path("api/v2/threads/<str:thread_id>/votes/", ThreadVoteView.as_view(), name="thread-vote"),
    path("api/v2/comments/<str:comment_id>/votes/", CommentVoteView.as_view(), name="comment-vote"),
]
