"""
URLs for forum.
"""

from django.urls import include, path

from forum.views.proxy import ForumProxyAPIView

api_patterns = [
    # Proxy view for various API endpoints
    path("<path:suffix>", ForumProxyAPIView.as_view(), name="forum_proxy"),
]

urlpatterns = [
    path("api/v2/", include(api_patterns)),
]
