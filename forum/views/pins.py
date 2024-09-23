"""Forum Pin/Unpin thread API Views."""

from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.backends.mongodb.api import handle_pin_unpin_thread_request
from forum.serializers.thread import ThreadSerializer


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
            thread_data: dict[str, Any] = handle_pin_unpin_thread_request(
                request.data.get("user_id", ""), thread_id, "pin", ThreadSerializer
            )
        except ValueError as e:
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
            thread_data: dict[str, Any] = handle_pin_unpin_thread_request(
                request.data.get("user_id", ""),
                thread_id,
                "unpin",
                ThreadSerializer,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(thread_data, status=status.HTTP_200_OK)
