"""Forum Threads API Views."""

import logging
from typing import Any, Optional

from bson import ObjectId
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from forum.models import Comment, CommentThread
from forum.models.model_utils import validate_object
from forum.serializers.comment import CommentSerializer
from forum.serializers.thread import ThreadSerializer
from forum.utils import str_to_bool

log = logging.getLogger(__name__)


class ThreadsAPIView(APIView):
    """
    API view to handle operations related to threads.

    This view uses the CommentThread model for database interactions and the ThreadSerializer
    for serializing and deserializing data.
    """

    def get(self, request, thread_id: str) -> Response:
        """
        Retrieve a thread by its ID.

        Args:
            request: The HTTP request object.
            thread_id: The ID of the thread to retrieve.

        Returns:
            Response: A Response object containing the serialized thread data or an error message.
        """
        try:
            # params = {
            #     "recursive": True,
            #     "with_responses": True,
            #     "mark_as_read": False,
            #     "reverse_order": "true",
            #     "merge_question_type_responses": False,
            #     # "request_id": UUID("d90e2606-23b8-4346-91d8-0654ec814b1b"),
            # }
            # params = {
            #     "recursive": False,
            #     "with_responses": True,
            #     "user_id": 6,
            #     "mark_as_read": False,
            #     "resp_skip": 0,
            #     "resp_limit": 10,
            #     "reverse_order": "true",
            #     "merge_question_type_responses": False,
            #     # "request_id": UUID("99d6c3ca-e07b-4bf6-a78e-ffec96e4bd15"),
            # }
            params = request.query_params
            thread = validate_object(CommentThread, thread_id)
            if not thread:
                return Response(
                    {"detail": "Thread not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            thread_data = {
                **thread,
                "id": str(thread.get("_id")),
                "type": str(thread.get("_type", "")).lower(),
                "user_id": str(params.get("user_id", thread.get("user_id"))),
                "username": str(thread.get("author_username")),
            }
            if "resp_skip" in params:
                thread_data["resp_skip"] = params["resp_skip"]
            if "resp_limit" in params:
                thread_data["resp_limit"] = params["resp_limit"]
            serializer = ThreadSerializer(
                data=thread_data,
                context={
                    "recursive": params.get("recursive", False),
                    "with_responses": params.get("with_responses", True),
                    "include_endorsed": True,
                    "include_read_state": True,
                    "mark_as_read": params.get("mark_as_read", False),
                    "reverse_order": params.get("reverse_order", True),
                    "user_id": params.get("user_id"),
                    "merge_question_type_responses": params.get(
                        "merge_question_type_responses", False
                    ),
                },
            )
            if not serializer.is_valid(raise_exception=True):
                log.error(
                    f"\n\n ValidationError(serializer.errors):: {serializer.errors}"
                )
                raise ValidationError(serializer.errors)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

