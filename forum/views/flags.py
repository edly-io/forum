"""Forum Flag API Views."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.models import Comment, CommentThread, Users
from forum.models.model_utils import (
    flag_as_abuse,
    un_flag_all_as_abuse,
    un_flag_as_abuse,
)
from forum.serializers.comment import CommentSerializer
from forum.serializers.thread import ThreadSerializer


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
        comment = Comment().get(comment_id)
        if not (user and comment):
            return Response(
                {"error": "User / Comment doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action == "flag":
            updated_comment = flag_as_abuse(user, comment)
        elif action == "unflag":
            if request_data.get("all") and request_data.get("all") is True:
                updated_comment = un_flag_all_as_abuse(comment)
            else:
                updated_comment = un_flag_as_abuse(user, comment)
        else:
            return Response(
                {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
            )

        if updated_comment is None:
            return Response(
                {"error": "Failed to update comment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        context = {
            "id": str(updated_comment["_id"]),
            **updated_comment,
            "user_id": user["_id"],
            "username": user["username"],
            "type": "comment",
            "thread_id": str(updated_comment.get("comment_thread_id", None)),
        }
        serializer = CommentSerializer(context)
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
        thread = CommentThread().get(thread_id)
        if not (user and thread):
            return Response(
                {"error": "User / Thread doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action == "flag":
            updated_thread = flag_as_abuse(user, thread)
        elif action == "unflag":
            if request_data.get("all"):
                updated_thread = un_flag_all_as_abuse(thread)
            else:
                updated_thread = un_flag_as_abuse(user, thread)
        else:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if updated_thread is None:
            return Response(
                {"error": "Failed to update thread"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        context = {
            "id": str(updated_thread["_id"]),
            **updated_thread,
            "user_id": user["_id"],
            "username": user["username"],
            "type": "thread",
            "thread_id": str(updated_thread.get("comment_thread_id", None)),
        }
        serializer = ThreadSerializer(context)
        return Response(serializer.data, status=status.HTTP_200_OK)
