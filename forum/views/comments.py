"""Forum Comments API Views."""

from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from forum.models import Comment, CommentThread
from forum.models.model_utils import validate_object
from forum.serializers.comment import UserCommentSerializer
from forum.utils import str_to_bool


def validate_comments_request_data(data: dict[str, Any]) -> None:
    """
    Validates the request data if it exists or not.

    Parameters:
        data: request data to validate.
    Response:
        raise exception if some data does not exists.
    """
    fields_to_validate = ["body", "course_id", "user_id"]
    for field in fields_to_validate:
        if field not in data or not data[field]:
            raise ValueError(f"{field} is missing.")


def create_comment(
    data: dict[str, Any],
    depth: int,
    thread_id: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> Any:
    """handle comment creation and returns a comment"""
    new_comment_id = Comment().insert(
        body=data["body"],
        course_id=data["course_id"],
        anonymous=data.get("anonymous", False),
        anonymous_to_peers=data.get("anonymous_to_peers", False),
        author_id=data["user_id"],
        comment_thread_id=thread_id,
        parent_id=parent_id,
        depth=depth,
    )
    return Comment().get(new_comment_id)


def prepare_comment_api_response(
    comment: dict[str, Any],
    exclude_fields: Optional[list[str]] = None,
) -> dict[str, Any]:
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
        "type": str(comment.get("_type", "")).lower(),
    }
    serializer = UserCommentSerializer(
        data=comment_data,
        exclude_fields=exclude_fields,
    )
    if not serializer.is_valid():
        raise ValidationError(serializer.errors)

    return serializer.data


class CommentsAPIView(APIView):
    """
    API View to handle GET, POST, PUT, and DELETE requests for comments.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request, comment_id: str) -> Response:
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
            comment = validate_object(Comment, comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = prepare_comment_api_response(
            comment,
            exclude_fields=["sk"],
        )
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request, comment_id: str) -> Response:
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
        try:
            comment = validate_object(Comment, comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        try:
            validate_comments_request_data(data)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = create_comment(data, 1, parent_id=comment_id)
        try:
            if comment:
                response_data = prepare_comment_api_response(
                    comment,
                    exclude_fields=["endorsement", "sk"],
                )
                return Response(response_data, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"error": "Comment is not created"},
            status=status.HTTP_400_BAD_REQUEST,
        )

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
            comment = validate_object(Comment, comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data
        update_comment_data: dict[str, Any] = self._get_update_comment_data(data)
        if comment:
            update_comment_data["edit_history"] = comment.get("edit_history", [])
            update_comment_data["original_body"] = comment.get("body")

        Comment().update(comment_id, **update_comment_data)
        updated_comment = Comment().get(comment_id)
        try:
            if updated_comment:
                response_data = prepare_comment_api_response(
                    updated_comment,
                    exclude_fields=(
                        ["endorsement", "sk"]
                        if updated_comment.get("parent_id")
                        else ["sk"]
                    ),
                )
                return Response(response_data, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"error": "Comment is not updated"},
            status=status.HTTP_400_BAD_REQUEST,
        )

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
            comment = validate_object(Comment, comment_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Comment does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = prepare_comment_api_response(
            comment,
            exclude_fields=["endorsement", "sk"],
        )
        Comment().delete(comment_id)

        return Response(data, status=status.HTTP_200_OK)

    def _get_update_comment_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """convert request data to a dict excluding empty data"""

        fields = [
            ("body", data.get("body")),
            ("course_id", data.get("course_id")),
            ("anonymous", str_to_bool(data.get("anonymous", "False"))),
            (
                "anonymous_to_peers",
                str_to_bool(data.get("anonymous_to_peers", "False")),
            ),
            ("closed", str_to_bool(data.get("closed", "False"))),
            ("endorsed", str_to_bool(data.get("endorsed", "False"))),
            ("author_id", data.get("user_id")),
            ("editing_user_id", data.get("editing_user_id")),
            ("edit_reason_code", data.get("edit_reason_code")),
            ("endorsement_user_id", data.get("endorsement_user_id")),
        ]
        return {field: value for field, value in fields if value is not None}


class CreateThreadCommentAPIView(APIView):
    """
    API View to handle POST request for parent comments.
    """

    permission_classes = (AllowAny,)

    def post(self, request: Request, thread_id: str) -> Response:
        """
        Creates a new parent comment.

        Parameters:
            request (Request): The incoming request.
            thread_id: The ID of the thread for creating a comment on it.
        Body:
            body: The content of the comment.
            course_id: The Id of the respective course.
            user_id: The requesting user id.
            anonymous: anonymous flag(True or False).
            anonymous_to_peers: anonymous to peers flag(True or False).
        Response:
            The details of the comment that is created.
        """
        try:
            validate_object(CommentThread, thread_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Thread does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        try:
            validate_comments_request_data(data)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comment = create_comment(data, 0, thread_id=thread_id)
        try:
            if comment:
                response_data = prepare_comment_api_response(
                    comment,
                    exclude_fields=["endorsement", "sk"],
                )
                return Response(response_data, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"error": "Comment is not created"},
            status=status.HTTP_400_BAD_REQUEST,
        )
