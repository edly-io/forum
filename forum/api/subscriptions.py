"""
API for subscriptions.
"""

from typing import Any

from django.http import QueryDict
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from forum.backends.mongodb.api import (
    find_subscribed_threads,
    get_threads,
    subscribe_user,
    unsubscribe_user,
    validate_params,
)
from forum.backends.mongodb.subscriptions import Subscriptions
from forum.backends.mongodb.threads import CommentThread
from forum.backends.mongodb.users import Users
from forum.pagination import ForumPagination
from forum.serializers.subscriptions import SubscriptionSerializer
from forum.serializers.thread import ThreadSerializer
from forum.utils import ForumV2RequestError


def validate_user_and_thread(
    user_id: str, source_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Validate if user and thread exist.
    """
    user = Users().get(user_id)
    thread = CommentThread().get(source_id)
    if not (user and thread):
        raise ForumV2RequestError("User / Thread doesn't exist")
    return user, thread


def create_subscription(user_id: str, source_id: str) -> dict[str, Any]:
    """
    Create a subscription for a user.
    """
    _, thread = validate_user_and_thread(user_id, source_id)
    subscription = subscribe_user(user_id, source_id, thread["_type"])
    serializer = SubscriptionSerializer(subscription)
    return serializer.data


def delete_subscription(user_id: str, source_id: str) -> dict[str, Any]:
    """
    Delete a subscription for a user.
    """
    _, _ = validate_user_and_thread(user_id, source_id)

    subscription = Subscriptions().get_subscription(
        user_id,
        source_id,
    )
    if not subscription:
        raise ForumV2RequestError("Subscription doesn't exist")

    unsubscribe_user(user_id, source_id)
    serializer = SubscriptionSerializer(subscription)
    return serializer.data


def get_user_subscriptions(
    user_id: str, course_id: str, query_params: dict[str, Any]
) -> dict[str, Any]:
    """
    Get a user's subscriptions.
    """
    validate_params(query_params, user_id)
    thread_ids = find_subscribed_threads(user_id, course_id)
    threads = get_threads(query_params, ThreadSerializer, thread_ids, user_id)
    return threads


def get_thread_subscriptions(
    thread_id: str, page: int = 1, per_page: int = 20
) -> dict[str, Any]:
    """
    Retrieve subscriptions to a specific thread.

    Args:
        thread_id (str): The ID of the thread to retrieve subscriptions for.
        page (int): The page number for pagination.
        per_page (int): The number of items per page.

    Returns:
        dict: A dictionary containing the paginated subscription data.
    """
    query = {"source_id": thread_id, "source_type": "CommentThread"}
    subscriptions_list = list(Subscriptions().find(query))

    factory = APIRequestFactory()
    query_params = QueryDict("", mutable=True)
    query_params.update({"page": str(page), "per_page": str(per_page)})
    request = factory.get("/", query_params)
    drf_request = Request(request)

    paginator = ForumPagination()
    paginated_subscriptions = paginator.paginate_queryset(
        subscriptions_list, drf_request
    )

    subscriptions = SubscriptionSerializer(paginated_subscriptions, many=True)
    subscriptions_count = len(subscriptions.data)

    return {
        "collection": subscriptions.data,
        "subscriptions_count": subscriptions_count,
        "page": page,
        "num_pages": max(1, subscriptions_count // per_page),
    }
