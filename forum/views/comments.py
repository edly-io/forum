"""Forum Comments API Views."""

import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from forum.models import Comment
from forum.serializers.comments_api import (
    CommentsAPIGetSerializer,
    CommentsAPIPostAndDeleteSerializer,
)
from forum.utils import str_to_bool

log = logging.getLogger(__name__)


class CommentsAPIView(APIView):
    """
    API View to handle GET, POST, PUT, and DELETE requests for comments.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request, comment_id: str = None) -> Response:
        """
        Retrieves a parent comment.
        For chile comments, below API is called that return all child comments in children field
        url: http://localhost:8000/forum/api/v2/threads/66ab94950dead7001deb947a
        """
        try:
            comment = Comment().get(comment_id)
            if not comment:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        data = self._prepare_response("get", comment)
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request, comment_id: str = None) -> Response:
        """
        Creates a new child comment.
        For parent comment below API is called.
        url: http://localhost:8000/forum/api/v2/threads/66ab94950dead7001deb947a/comments
        """
        data = request.data
        # TODO validations
        new_comment_id = Comment().insert(
            body=data.get("body"),
            course_id=data.get("course_id"),
            anonymous=data.get("anonymous", False),
            anonymous_to_peers=data.get("anonymous_to_peers", False),
            author_id=data.get("user_id"),
            parent_id=comment_id,
            depth=1,
        )
        comment = Comment().get(new_comment_id)
        data = self._prepare_response("post", comment)

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request: Request, comment_id: str) -> Response:
        """
        Update an existing child and parent comment.
        """
        try:
            comment = Comment().get(comment_id)
            if not comment:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.POST.dict()
        update_comment_data: dict[str, Any] = {
            "body": data.get("body", comment.get("body", "")),
            "anonymous": str_to_bool(data.get("anonymous", False)),
            "anonymous_to_peers": str_to_bool(data.get("anonymous_to_peers", False)),
            "course_id": data.get("course_id", ""),
            "closed": str_to_bool(data.get("closed", False)),
            "author_id": data.get("user_id"),
            "endorsed": str_to_bool(data.get("endorsed", False)),
        }
        if "editing_user_id" in data:
            update_comment_data["editing_user_id"] = data.get("editing_user_id")

        if "edit_reason_code" in data:
            update_comment_data["edit_reason_code"] = data.get("edit_reason_code")

        if "endorsement_user_id" in data:
            update_comment_data["endorsement_user_id"] = data.get("endorsement_user_id")

        update_comment_data["edit_history"] = comment.get("edit_history", [])
        update_comment_data["original_body"] = comment.get("body")

        Comment().update(comment_id, **update_comment_data)
        updated_comment = Comment().get(comment_id)
        data = self._prepare_response("put", updated_comment)

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request: Request, comment_id: str) -> Response:
        """
        Delete a comment.
        """
        try:
            comment = Comment().get(comment_id)
            if not comment:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        data = self._prepare_response("delete", comment)
        Comment().delete(comment_id)

        return Response(data, status=status.HTTP_200_OK)

    def _prepare_response(self, method, comment):
        comment_data = {
            **comment,
            "id": str(comment.get("_id")),
            "user_id": comment.get("author_id"),
            "thread_id": str(comment.get("comment_thread_id")),
            "username": comment.get("author_username"),
            "parent_id": str(comment.get("parent_id")),
            "type": comment.get("_type").lower(),
        }
        if method == "get":
            serializer = CommentsAPIGetSerializer(data=comment_data)
        elif method == "post":
            serializer = CommentsAPIPostAndDeleteSerializer(data=comment_data)
        elif method == "put":
            if comment.get("parent_id"):
                serializer = CommentsAPIPostAndDeleteSerializer(data=comment_data)
            else:
                serializer = CommentsAPIGetSerializer(data=comment_data)
        else:
            serializer = CommentsAPIPostAndDeleteSerializer(data=comment_data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        return serializer.data
