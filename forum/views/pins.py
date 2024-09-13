"""Forum Pin/Unpin thread API Views."""

import logging
from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.backends.mongodb.api import handle_pin_unpin_thread_request
from forum.serializers.thread import ThreadSerializer
from forum.utils import ForumV2RequestError

log = logging.getLogger(__name__)


def pin_unpin_thread(
    user_id: str,
    thread_id: str,
    action: str,
) -> dict[str, Any]:
    """Pin or Unpin  a thread."""
    try:
        thread_data: dict[str, Any] = handle_pin_unpin_thread_request(
            user_id, thread_id, action, ThreadSerializer
        )
    except ValueError as e:
        log.error(f"Forumv2RequestError for {action} thread request.")
        raise ForumV2RequestError(str(e)) from e

    return thread_data


class PinThreadAPIView(APIView):
    """
    API View to Pin thread.
    Handles PUT requests to pin a thread.
    """

    permission_classes = (AllowAny,)

    def put(self, request: Request, thread_id: str) -> Response:
        """
        Pins a thread.
        Parameters:
            request (Request): The incoming request.
            thread_id (str): The ID of the thread to pin.
        Body:
            user_id: requesting user's id
        Response:
            A response with the updated thread data.
        """
        try:
            thread_data: dict[str, Any] = pin_unpin_thread(
                request.data.get("user_id", ""), thread_id, "pin"
            )
        except ForumV2RequestError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(thread_data, status=status.HTTP_200_OK)


class UnpinThreadAPIView(APIView):
    """
    API View to Unpin a thread.
    Handles PUT requests to unpin a thread.
    """

    permission_classes = (AllowAny,)

    def put(self, request: Request, thread_id: str) -> Response:
        """
        Unpins a thread.
        Parameters:
            request (Request): The incoming request.
            thread_id (str): The ID of the thread to unpin.
        Body:
            user_id: requesting user's id
        Response:
            A response with the updated thread data.
        """
        try:
            thread_data: dict[str, Any] = pin_unpin_thread(
                request.data.get("user_id", ""), thread_id, "unpin"
            )
        except ForumV2RequestError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(thread_data, status=status.HTTP_200_OK)
