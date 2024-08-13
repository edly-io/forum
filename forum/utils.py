"""Forum Utils."""

import logging
from typing import Any, Dict, Tuple

import requests
from django.conf import settings
from django.http import HttpRequest
from requests.models import Response

from forum.models import CommentThread, Users
from forum.serializers.thread import UserThreadSerializer

logger = logging.getLogger(__name__)


def handle_proxy_requests(request: HttpRequest, suffix: str, method: str) -> Response:
    """
    Catches all requests and sends them to forum/cs_comments_service URLs.

    Arguments:
        request (HttpRequest): The incoming HTTP request.
        suffix (str): The URL suffix for the target service.
        method (str): The HTTP method to use for the proxy request.

    Returns:
        Response: The response from the proxied service.
    """
    comments_service_url = f"http://forum:{settings.FORUM_PORT}"
    url = f"{comments_service_url}/api/v1/{suffix}"
    request_headers = {
        "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key"),
        "Accept-Language": request.headers.get("Accept-Language"),
    }
    request_data = request.POST.dict()
    request_params = request.GET.dict()

    logger.info(f"{method} request to cs_comments_service url: {url}")
    return requests.request(
        method,
        url,
        data=request_data,
        params=request_params,
        headers=request_headers,
        timeout=5.0,
    )


def validate_thread_and_user(
    user_id: str, thread_id: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate thread and user.

    Arguments:
        user_id (str): The ID of the user making the request.
        thread_id (str): The ID of the thread.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing the user and thread data.

    Raises:
        ValueError: If the thread or user is not found.
    """
    thread = CommentThread().get(thread_id)
    user = Users().get(user_id)
    if not (thread and user):
        raise ValueError("User / Thread doesn't exist")

    return user, thread


def pin_unpin_thread(thread_id: str, action: str) -> None:
    """
    Pin or unpin the thread based on action parameter.

    Arguments:
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").
    """
    CommentThread().update(thread_id, pinned=action == "pin")


def get_pinned_unpinned_thread_serialized_data(
    user: Dict[str, Any], thread_id: str
) -> Dict[str, Any]:
    """
    Return serialized data of pinned or unpinned thread.

    Arguments:
        user (Dict[str, Any]): The user who requested the action.
        thread_id (str): The ID of the thread to pin/unpin.

    Returns:
        Dict[str, Any]: The serialized data of the pinned/unpinned thread.

    Raises:
        ValueError: If the serialization is not valid.
    """
    updated_thread = CommentThread().get(thread_id)
    context = {
        "user_id": user["_id"],
        "username": user["username"],
        "type": "thread",
        "id": thread_id,
    }
    if updated_thread is not None:
        context = {**context, **updated_thread}
    serializer = UserThreadSerializer(data=context)
    if not serializer.is_valid():
        raise ValueError(serializer.errors)

    return serializer.data


def handle_pin_unpin_thread_request(
    user_id: str, thread_id: str, action: str
) -> Dict[str, Any]:
    """
    Catches pin/unpin thread request.

    - validates thread and user.
    - pin or unpin the thread based on action parameter.
    - return serialized data of thread.

    Arguments:
        user_id (str): The ID of the user making the request.
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").

    Returns:
        Dict[str, Any]: The serialized data of the pinned/unpinned thread.
    """
    user, _ = validate_thread_and_user(user_id, thread_id)
    pin_unpin_thread(thread_id, action)
    return get_pinned_unpinned_thread_serialized_data(user, thread_id)
