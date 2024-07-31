"""Forum Views."""

import logging

import requests
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class ForumProxyAPIView(APIView):
    """
    An Proxy API View to Redirect All API requests to forum/cs_comments_service urls.
    """

    permission_classes = (AllowAny,)
    COMMENTS_SERVICE_URL = f"http://forum:{settings.FORUM_PORT}"

    def post(self, request, suffix):
        """
        Catches post requests and sends it to forum/cs_comments_service post urls.
        """
        request_headers = {
            "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key"),
            "Accept-Language": request.headers.get("Accept-Language"),
        }
        request_data = request.data
        url = self.COMMENTS_SERVICE_URL + suffix

        """
        Will be removed once start migrating the endpoints.
        login on postman before using this curl request.
        sample curl request to /:commentable_id/threads POST:
        curl --location 'http://local.edly.io:8000/forum/forum_proxy/api/v1/course123/threads/' \
            --header 'X-Csrftoken: kjGJPW6nPDGpHd23bBtlPhlQYooctsDDuH9SycovPI7vdWODBAstmbT1HaGWgX7Z' \
            --header 'X-Edx-Api-Key: forumapikey' \
            --header 'Accept-Language: en' \
            --header 'Content-Type: application/json' \
            --data '{
                "body": "<p>test post request 1</p>",
                "anonymous": false,
                "anonymous_to_peers": false,
                "course_id": "course-v1:Arbisoft+SE002+2024_S2",
                "commentable_id": "course",
                "thread_type": "discussion",
                "title": "Test"
            }'
        Uncomment below lines of code if want to test above curl request,
        when called from edx-platform suffix should have required params
        """
        # user_id = request.user.id
        # url = url + (f"&user_id={user_id}" if "?" in url else f"?user_id={user_id}")

        logger.info(f"Post Request to cs_comments_service url: {url}")
        response = requests.post(url, data=request_data, headers=request_headers)
        return Response(data=response.json(), status=response.status_code)

    def get(self, request, suffix):
        """
        Catches get requests and sends it to forum/cs_comments_service get urls.
        """
        request_headers = {
            "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key"),
            "Accept-Language": request.headers.get("Accept-Language"),
        }
        request_data = request.data
        url = self.COMMENTS_SERVICE_URL + suffix

        """
        Will be removed once start migrating the endpoints.
        sample curl request to /:commentable_id/threads GET:
        curl --location --request GET 'http://local.edly.io:8000/forum/forum_proxy/api/v1/course123/threads/' \
            --header 'X-Edx-Api-Key: forumapikey' \
            --header 'Accept-Language: en' \
            --header 'Content-Type: application/json' \
            --data '{
                "course_id": "course-v1:Arbisoft+SE002+2024_S2",
                "commentable_id": "course123"
            }'
        Uncomment below lines of code if want to test above curl request,
        when called from edx-platform suffix should have required params
        """
        # course_id = request_data.get("course_id")
        # url = url + (f"&course_id={course_id}" if "?" in url else f"?course_id={course_id}")

        logger.info(f"Get Request to cs_comments_service url: {url}")
        response = requests.get(url, data=request_data, headers=request_headers)
        return Response(data=response.json(), status=response.status_code)

    def delete(self, request, suffix):
        """
        Catches delete requests and sends it to forum/cs_comments_service delete urls.
        """
        request_headers = {
            "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key"),
            "Accept-Language": request.headers.get("Accept-Language"),
        }
        request_data = request.data
        url = self.COMMENTS_SERVICE_URL + suffix

        """
        Will be removed once start migrating the endpoints.
        sample curl request to /:commentable_id/threads DELETE:
        curl --location --request DELETE 'http://local.edly.io:8000/forum/forum_proxy/api/v1/course123/threads/' \
            --header 'X-Edx-Api-Key: forumapikey' \
            --header 'Accept-Language: en' \
            --data ''
        """

        logger.info(f"Get Request to cs_comments_service url: {url}")
        response = requests.delete(url, data=request_data, headers=request_headers)
        return Response(data=response.json(), status=response.status_code)

    def put(self, request, suffix):
        """
        Catches post requests and sends it to forum/cs_comments_service post urls.
        """
        request_headers = {
            "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key"),
            "Accept-Language": request.headers.get("Accept-Language"),
        }
        request_data = request.data
        url = self.COMMENTS_SERVICE_URL + suffix

        """
        Will be removed once start migrating the endpoints.
        sample curl request to /threads/:thread_id PUT:
        curl --location --request PUT
        'http://local.edly.io:8000/forum/forum_proxy/api/v1/threads/66a9d1cca99edf001d4c5f77/' \
            --header 'X-Edx-Api-Key: forumapikey' \
            --header 'Accept-Language: en' \
            --header 'Content-Type: application/json' \
            --data '{
                "body": "<p>test post request 11</p>"
            }'
        """

        logger.info(f"Put Request to cs_comments_service url: {url}")
        response = requests.put(url, data=request_data, headers=request_headers)
        return Response(data=response.json(), status=response.status_code)
