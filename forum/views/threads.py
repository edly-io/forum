"""Forum Threads API Views."""

import logging
from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from forum.models.comments import Comment
from forum.models.model_utils import (
    delete_comments_of_a_thread,
    get_threads,
    validate_object,
    validate_params,
)
from forum.models.threads import CommentThread
from forum.serializers.thread import ThreadSerializer
from forum.utils import get_int_value_from_collection, str_to_bool

log = logging.getLogger(__name__)


def get_thread_data(thread: dict[str, Any]) -> dict[str, Any]:
    """Prepare thread data for the api response."""
    _type = str(thread.get("_type", "")).lower()
    thread_data = {
        **thread,
        "id": str(thread.get("_id")),
        "type": "thread" if _type == "commentthread" else _type,
        "user_id": thread.get("author_id"),
        "username": str(thread.get("author_username")),
        "comments_count": thread["comment_count"],
    }
    return thread_data


def prepare_thread_api_response(
    thread: dict[str, Any],
    include_context: Optional[bool] = False,
    data_or_params: Optional[dict[str, Any]] = None,
    include_data_from_params: Optional[bool] = False,
) -> dict[str, Any] | None:
    """Serialize thread data for the api response."""
    thread_data = get_thread_data(thread)

    context = {}
    if include_context:
        context = {
            "include_endorsed": True,
            "include_read_state": True,
        }
        if data_or_params:
            if include_data_from_params:
                thread_data["resp_skip"] = get_int_value_from_collection(
                    data_or_params, "resp_skip", 0
                )
                thread_data["resp_limit"] = get_int_value_from_collection(
                    data_or_params, "resp_limit", 100
                )
                context["recursive"] = str_to_bool(
                    data_or_params.get("recursive", "False")
                )
                context["with_responses"] = str_to_bool(
                    data_or_params.get("with_responses", "True")
                )
                context["mark_as_read"] = str_to_bool(
                    data_or_params.get("mark_as_read", "False")
                )
                context["reverse_order"] = str_to_bool(
                    data_or_params.get("reverse_order", "True")
                )
                context["merge_question_type_responses"] = str_to_bool(
                    data_or_params.get("merge_question_type_responses", "False")
                )

            if user_id := data_or_params.get("user_id"):
                context["user_id"] = user_id

    serializer = ThreadSerializer(
        data=thread_data,
        context=context,
    )
    if not serializer.is_valid(raise_exception=True):
        log.error(f"validation error in thread API call: {serializer.errors}")
        raise ValidationError(serializer.errors)

    return serializer.data


class ThreadsAPIView(APIView):
    """
    API view to handle operations related to threads.

    This view uses the CommentThread model for database interactions and the ThreadSerializer
    for serializing and deserializing data.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request, thread_id: str) -> Response:
        """
        Retrieve a thread by its ID.

        Args:
            request: The HTTP request object.
            thread_id: The ID of the thread to retrieve.

        Returns:
            Response: A Response object containing the serialized thread data or an error message.
        """
        try:
            thread = validate_object(CommentThread, thread_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Thread does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        params = request.query_params
        try:
            serialized_data = prepare_thread_api_response(thread, True, params, True)
            return Response(serialized_data)

        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request: Request, thread_id: str) -> Response:
        """
        Deletes a thread by it's ID.

        Parameters:
            request (Request): The incoming request.
            thread_id: The ID of the thread to be deleted.
        Body:
            Empty.
        Response:
            The details of the thread that is deleted.
        """
        try:
            thread = validate_object(CommentThread, thread_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "thread does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delete_comments_of_a_thread(thread_id)
        thread = validate_object(CommentThread, thread_id)

        try:
            serialized_data = prepare_thread_api_response(thread)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        CommentThread().delete(thread_id)

        return Response(serialized_data, status=status.HTTP_200_OK)

    def put(self, request: Request, thread_id: str) -> Response:
        """
        Updates an existing thread.

        Parameters:
            request (Request): The incoming request.
            thread_id: The ID of the thread to be edited.
        Body:
            fields to be updated.
        Response:
            The details of the thread that is updated.
        """
        try:
            thread = validate_object(Comment, thread_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "thread does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        update_thread_data: dict[str, Any] = self._get_update_thread_data(data)
        if thread:
            update_thread_data["edit_history"] = thread.get("edit_history", [])
            update_thread_data["original_body"] = thread.get("body")

        CommentThread().update(thread_id, **update_thread_data)
        updated_thread = CommentThread().get(thread_id)
        try:
            if updated_thread:
                serialized_data = prepare_thread_api_response(
                    updated_thread,
                    True,
                    data,
                )
                return Response(serialized_data, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"error": "Thread is not updated"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _get_update_thread_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """convert request data to a dict excluding empty data"""
        fields = [
            ("title", data.get("title")),
            ("body", data.get("body")),
            ("course_id", data.get("course_id")),
            ("anonymous", str_to_bool(data.get("anonymous", "False"))),
            (
                "anonymous_to_peers",
                str_to_bool(data.get("anonymous_to_peers", "False")),
            ),
            ("closed", str_to_bool(data.get("closed", "False"))),
            ("commentable_id", data.get("commentable_id", "course")),
            ("author_id", data.get("user_id")),
            ("editing_user_id", data.get("editing_user_id")),
            ("pinned", str_to_bool(data.get("pinned", "False"))),
            ("thread_type", data.get("thread_type", "discussion")),
            ("edit_reason_code", data.get("edit_reason_code")),
        ]
        return {field: value for field, value in fields if value is not None}


class CreateThreadAPIView(APIView):
    """
    API view to create a new thread.

    This view uses the CommentThread model for database interactions and the ThreadSerializer
    for serializing and deserializing data.
    """

    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        """
        Create a new thread.

        Parameters:
            request (Request): The incoming request.
        Body:
            fields to be added in a new thread.
        Response:
            The details of the thread that is created.
        """
        data = request.data
        try:
            self.validate_request_data(data)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = self.create_thread(data)
        try:
            serialized_data = prepare_thread_api_response(thread, True, data)
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(serialized_data, status=status.HTTP_200_OK)

    def validate_request_data(self, data: dict[str, Any]) -> None:
        """
        Validates the request data if it exists or not.

        Parameters:
            data: request data to validate.
        Response:
            raise exception if some data does not exists.
        """
        fields_to_validate = ["title", "body", "course_id", "user_id"]
        for field in fields_to_validate:
            if field not in data or not data[field]:
                raise ValueError(f"{field} is missing.")

    def create_thread(self, data: dict[str, Any]) -> Any:
        """handle thread creation and returns a thread."""
        new_comment_id = CommentThread().insert(
            title=data["title"],
            body=data["body"],
            course_id=data["course_id"],
            anonymous=str_to_bool(data.get("anonymous", "False")),
            anonymous_to_peers=str_to_bool(data.get("anonymous_to_peers", "False")),
            author_id=data["user_id"],
            commentable_id=data.get("commentable_id", "course"),
            thread_type=data.get("thread_type", "discussion"),
        )
        return CommentThread().get(new_comment_id)


class UserThreadsAPIView(APIView):
    """
    API View for getting all threads of a course.

    This view provides an endpoint for retrieving all threads based on course id.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """
        Retrieve a course's threads.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A Response object with the threads data.

        Raises:
            HTTP_400_BAD_REQUEST: If the user does not exist.
        """
        params = request.GET.dict()
        validations = validate_params(params)
        if validations:
            return validations

        user_id = params.get("user_id", "")
        course_id = params.get("course_id")
        thread_filter = {
            "_type": {"$in": [CommentThread.content_type]},
            "course_id": {"$in": [course_id]},
        }
        filtered_threads = CommentThread().find(thread_filter)
        thread_ids = [thread["_id"] for thread in filtered_threads]
        threads = get_threads(params, user_id, ThreadSerializer, thread_ids, True)
        return Response(data=threads, status=status.HTTP_200_OK)
