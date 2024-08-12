"""Forum Pin/Unpin thread API Views."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.utils import handle_pin_unpin_thread_request


class PinThreadAPIView(APIView):
    """
    API View to Pin thread.

    Handles PUT requests to pin a thread.
    """

    permission_classes = (AllowAny,)

    def put(self, request, thread_id):
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
        thread_data = handle_pin_unpin_thread_request(
            request.data.get("user_id"), thread_id, "pin"
        )

        return Response(thread_data, status=status.HTTP_200_OK)


class UnpinThreadAPIView(APIView):
    """
    API View to Unpina a thread.

    Handles PUT requests to unpin a thread.
    """

    permission_classes = (AllowAny,)

    def put(self, request, thread_id):
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
        thread_data = handle_pin_unpin_thread_request(
            request.data.get("user_id"), thread_id, "unpin"
        )
        return Response(thread_data, status=status.HTTP_200_OK)
