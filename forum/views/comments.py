"""Forum Comments API Views."""

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from forum.models import Comment
from forum.serializers.comments_api import CommentsAPISerializer
from forum.utils import str_to_bool


class CommentsAPIView(APIView):
    """
    API View to handle GET, POST, PUT, and DELETE requests for comments.
    """

    permission_classes = (AllowAny,)

    def _validate_comment(self, comment_id):
        """
        Validates the comment if it exists or not.

        Parameters:
            comment_id: The ID of the comment.
        Response:
            comment object for the given comment_id.
        """
        comment = Comment().get(comment_id)
        if not comment:
            raise ObjectDoesNotExist
        return comment

    def get(self, request: Request, comment_id: str = None) -> Response:
        """
        Retrieves a parent comment.
        For chile comments, below API is called that return all child comments in children field
        url: http://localhost:8000/forum/api/v2/threads/66ab94950dead7001deb947a

        Parameters:
            request (Request): The incoming request.
            comment_id: The ID of the comment.
        Body:
            Empty.
        Response:
            The details of the comment for the given comment_id.
        """
        try:
            comment = self._validate_comment(comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        data = self._prepare_response(comment, exclude_fields=["sk"])
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request, comment_id: str = None) -> Response:
        """
        Creates a new child comment.
        For parent comment below API is called.
        url: http://localhost:8000/forum/api/v2/threads/66ab94950dead7001deb947a/comments

        Parameters:
            request (Request): The incoming request.
            comment_id: The ID of the parent comment for creating it's child comment.
        Body:
            body: The content of the comment.
            course_id: The Id of the respective course.
            user_id: The requesting user id.
            anonymous: anonymous flag(True or False).
            anonymous_to_peers: anonymous to peers flag(True or False).
        Response:
            The details of the comment that is created.
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
        data = self._prepare_response(comment, exclude_fields=["endorsement", "sk"])

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request: Request, comment_id: str) -> Response:
        """
        Updates an existing child/parent comment.

        Parameters:
            request (Request): The incoming request.
            comment_id: The ID of the comment to be edited.
        Body:
            fields to be updated.
        Response:
            The details of the comment that is updated.
        """
        try:
            comment = self._validate_comment(comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.POST.dict()
        fields = [
            ("body", data.get("body")),
            ("course_id", data.get("course_id")),
            ("anonymous", str_to_bool(data.get("anonymous", False))),
            ("anonymous_to_peers", str_to_bool(data.get("anonymous_to_peers", False))),
            ("closed", str_to_bool(data.get("closed", False))),
            ("endorsed", str_to_bool(data.get("endorsed", False))),
            ("author_id", data.get("user_id")),
            ("editing_user_id", data.get("editing_user_id")),
            ("edit_reason_code", data.get("edit_reason_code")),
            ("endorsement_user_id", data.get("endorsement_user_id")),
        ]
        update_comment_data: dict[str, Any] = {
            field: value for field, value in fields if value is not None
        }
        update_comment_data["edit_history"] = comment.get("edit_history", [])
        update_comment_data["original_body"] = comment.get("body")

        Comment().update(comment_id, **update_comment_data)
        updated_comment = Comment().get(comment_id)
        data = self._prepare_response(
            updated_comment,
            exclude_fields=(
                ["endorsement", "sk"] if updated_comment.get("parent_id") else ["sk"]
            ),
        )

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request: Request, comment_id: str) -> Response:
        """
        Deletes a comment.

        Parameters:
            request (Request): The incoming request.
            comment_id: The ID of the comment to be deleted.
        Body:
            Empty.
        Response:
            The details of the comment that is deleted.
        """
        try:
            comment = self._validate_comment(comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        data = self._prepare_response(comment, exclude_fields=["endorsement", "sk"])
        Comment().delete(comment_id)

        return Response(data, status=status.HTTP_200_OK)

    def _prepare_response(self, comment, exclude_fields=[]):
        """
        Return serialized validated data.

        Parameters:
            comment: The comment details that needs to be serialized.
            exclude_fields: Any fields that need to be excluded from response.

        Response:
            serialized validated data of the comment.
        """
        comment_data = {
            **comment,
            "id": str(comment.get("_id")),
            "user_id": comment.get("author_id"),
            "thread_id": str(comment.get("comment_thread_id")),
            "username": comment.get("author_username"),
            "parent_id": str(comment.get("parent_id")),
            "type": comment.get("_type").lower(),
        }
        serializer = CommentsAPISerializer(
            data=comment_data, exclude_fields=exclude_fields
        )
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        return serializer.validated_data
