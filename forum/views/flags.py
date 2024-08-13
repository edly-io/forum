"""Forum Flag API Views."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.models.contents import Contents
from forum.models.model_utils import flag_as_abuse, un_flag_all_as_abuse, un_flag_as_abuse
from forum.models.users import Users
from forum.serializers.contents import ContentSerializer


class CommentFlagAPIView(APIView):
    """
    API View for flagging/unflagging comments.

    Handles PUT requests to flag or unflag a comment.
    """

    permission_classes = (AllowAny,)

    def put(self, request: Request, comment_id: str, action: str) -> Response:
        """
        Flag or unflag a comment.

        Parameters:
        request (Request): The incoming request.
        comment_id (str): The ID of the comment to flag/unflag.
        action (str): The action to take (either "flag" or "unflag").

        Returns:
        Response: A response with the updated comment data.
        """
        request_data = request.data
        user = Users().get(request_data["user_id"])
        content = Contents().get(comment_id)
        if not (user and content):
            return Response(
                {"error": "User / Comment doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if action == "flag":
            comment = flag_as_abuse(user, content)
        elif action == "unflag":
            if request_data.get("all") and request_data.get("all") is True:
                comment = un_flag_all_as_abuse(content)
            else:
                comment = un_flag_as_abuse(user, content)
        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ContentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ThreadFlagAPIView(APIView):
    """
    API View for flagging/unflagging threads.

    Handles PUT requests to flag or unflag a thread.
    """

    permission_classes = (AllowAny,)

    def put(self, request: Request, thread_id: str, action: str) -> Response:
        """
        Flag or unflag a thread.

        Parameters:
        request (Request): The incoming request.
        thread_id (str): The ID of the thread to flag/unflag.
        action (str): The action to take (either "flag" or "unflag").

        Returns:
        Response: A response with the updated thread data.
        """
        request_data = request.data
        user = Users().get(request_data["user_id"])
        content = Contents().get(thread_id)
        if not (user and content):
            return Response(
                {"error": "User / Comment doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if action == "flag":
            thread = flag_as_abuse(user, content)
        elif action == "unflag":
            if request_data.get("all"):
                thread = un_flag_all_as_abuse(content)
            else:
                thread = un_flag_as_abuse(user, content)
        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ContentSerializer(thread)
        return Response(serializer.data, status=status.HTTP_200_OK)
