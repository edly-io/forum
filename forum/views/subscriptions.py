"""Subscriptions API Views."""

from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.models import CommentThread, Subscriptions, Users
from forum.models.model_utils import (
    find_subscribed_threads,
    get_threads,
    subscribe_user,
    unsubscribe_user,
    validate_params,
)
from forum.pagination import ForumPagination
from forum.serializers.subscriptions import SubscriptionSerializer
from forum.serializers.thread import ThreadSerializer


class SubscriptionAPIView(APIView):
    """
    API View for managing subscriptions.

    This view provides endpoints for subscribing and unsubscribing users to/from sources.
    """

    permission_classes = (AllowAny,)

    def post(self, request: Request, user_id: str) -> Response:
        """
        Subscribe a user to a source.

        Args:
            request (HttpRequest): The HTTP request object.
            user_id (str): The ID of the user to subscribe.

        Returns:
            Response: A Response object with the subscription data.

        Raises:
            HTTP_400_BAD_REQUEST: If the user or content does not exist.
        """
        request_data = request.data
        user = Users().get(user_id)
        thread = None
        if request_data.get("source_id"):
            thread = CommentThread().get(request_data["source_id"])
        if not (user and thread):
            return Response(
                {"error": "User / Thread doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = subscribe_user(
            user_id, request_data["source_id"], thread["_type"]
        )
        serializer = SubscriptionSerializer(subscription)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, user_id: str) -> Response:
        """
        Unsubscribe a user from a source.

        Args:
            request (HttpRequest): The HTTP request object.
            user_id (str): The ID of the user to unsubscribe.

        Returns:
            Response: A Response object with the subscription data.

        Raises:
            HTTP_400_BAD_REQUEST: If the user or subscription does not exist.
        """
        params = request.GET.dict()
        user = Users().get(user_id)
        if not user:
            return Response(
                {"error": "User doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not params.get("source_id"):
            return Response(
                {"error": "Missing required parameter source_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription = Subscriptions().get_subscription(
            user_id,
            params["source_id"],
        )
        if not subscription:
            return Response(
                {"error": "Subscription doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        unsubscribe_user(user_id, params["source_id"])
        serializer = SubscriptionSerializer(subscription)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserSubscriptionAPIView(APIView):
    """
    API View for managing user subscriptions.

    This view provides an endpoint for retrieving a user's subscriptions.
    """

    permission_classes = (AllowAny,)

    def get(self, request: Request, user_id: str) -> Response:
        """
        Retrieve a user's subscriptions.

        Args:
            request (HttpRequest): The HTTP request object.
            user_id (str): The ID of the user to retrieve subscriptions for.

        Returns:
            Response: A Response object with the subscription data.

        Raises:
            HTTP_400_BAD_REQUEST: If the user does not exist.
        """
        params = request.GET.dict()
        validations = validate_params(params, user_id)
        if validations:
            return validations

        thread_ids = find_subscribed_threads(user_id, params["course_id"])
        threads = get_threads(params, user_id, ThreadSerializer, thread_ids)
        return Response(data=threads, status=status.HTTP_200_OK)


class ThreadSubscriptionAPIView(APIView):
    """
    API View for managing thread subscriptions.

    This view provides an endpoint for retrieving subscriptions to a specific thread.
    """

    permission_classes = (AllowAny,)
    pagination_class = ForumPagination

    def get(self, request: Request, thread_id: str) -> Response:
        """
        Retrieve subscriptions to a specific thread.

        Args:
            request (HttpRequest): The HTTP request object.
            thread_id (str): The ID of the thread to retrieve subscriptions for.

        Returns:
            Response: A paginated Response object with the subscription data.
        """
        query = {}
        response = {
            "collection": [],
            "subscriptions_count": 0,
            "page": request.GET.get("page", 1),
            "num_pages": 0,
        }
        query["source_id"] = thread_id
        query["source_type"] = "CommentThread"
        subscriptions_list = list(Subscriptions().find(query))

        paginator = self.pagination_class()
        paginated_subscriptions: dict[str, Any] | None = paginator.paginate_queryset(
            subscriptions_list,
            request,
        )

        if not paginated_subscriptions:
            return Response(response, status=status.HTTP_200_OK)

        subscriptions = SubscriptionSerializer(paginated_subscriptions, many=True)
        subscriptions_count = len(subscriptions.data)
        response["collection"] = subscriptions.data
        response["subscriptions_count"] = subscriptions_count
        response["page"] = request.GET.get("page", 1)
        response["num_pages"] = max(
            1, subscriptions_count // int(request.GET.get("per_page", 20))
        )
        return Response(response, status=status.HTTP_200_OK)