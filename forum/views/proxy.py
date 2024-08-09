"""Forum Views."""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.utils import handle_proxy_requests


class ForumProxyAPIView(APIView):
    """
    An Proxy API View to Redirect All API requests to forum/cs_comments_service urls.
    """

    permission_classes = (AllowAny,)

    def post(self, request, suffix):
        """
        Catches post requests and sends it to forum/cs_comments_service post urls.
        """
        response = handle_proxy_requests(request, suffix, "post")
        return Response(data=response.json(), status=response.status_code)

    def get(self, request, suffix):
        """
        Catches get requests and sends it to forum/cs_comments_service get urls.
        """
        response = handle_proxy_requests(request, suffix, "get")
        return Response(data=response.json(), status=response.status_code)

    def delete(self, request, suffix):
        """
        Catches delete requests and sends it to forum/cs_comments_service delete urls.
        """
        response = handle_proxy_requests(request, suffix, "delete")
        return Response(data=response.json(), status=response.status_code)

    def put(self, request, suffix):
        """
        Catches post requests and sends it to forum/cs_comments_service post urls.
        """
        response = handle_proxy_requests(request, suffix, "put")
        return Response(data=response.json(), status=response.status_code)
