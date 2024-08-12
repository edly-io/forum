"""Forum Utils."""

import logging

from bson import ObjectId
import requests
from django.conf import settings

from forum.models.users import Users
from forum.models.threads import CommentThread
from forum.serializers.pins import PinUnpinThreadSerializer

logger = logging.getLogger(__name__)


def handle_proxy_requests(request, suffix, method):
    """
    Catches all requests and sends it to forum/cs_comments_service urls.
    """
    comments_service_url = f"http://forum:{settings.FORUM_PORT}"
    url = comments_service_url + suffix
    request_headers = {
        "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key"),
        "Accept-Language": request.headers.get("Accept-Language"),
    }
    request_data = request.POST.dict() or request.data
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


def validate_pin_unpin_thread_request_data(user_id, thread_id):
    """
    Validates thread and user.
    """
    thread = CommentThread().get(_id=ObjectId(thread_id))
    if not thread:
        raise ValueError("Thread not found")

    user = Users().get(_id=user_id)
    if not user:
        raise ValueError("User not found")
    return user, thread


def pin_unpin_thread(thread_id, action):
    """
    Pin or unpin the thread based on action parameter.
    """
    CommentThread().collection.update_one(
        {"_id": ObjectId(thread_id)},
        {"$set": {"pinned": True if action == "pin" else False}},
    )


def get_pinned_unpinned_thread_serialized_data(user, thread_id):
    """
    Return serialized data of pinned or unpinned thread.
    """
    updated_thread = CommentThread().get(_id=ObjectId(thread_id))
    context = {
        **updated_thread,
        "user_id": user["_id"],
        "username": user["username"],
        "type": "thread",
        "id": thread_id,
    }
    serializer = PinUnpinThreadSerializer(data=context)
    if not serializer.is_valid():
        raise ValueError(serializer.errors)

    return serializer.data


def handle_pin_unpin_thread_request(user_id, thread_id, action):
    """
    Catches pin/unpin thread request.
    - validates thread and user.
    - pin or unpin the thread based on action parameter.
    - return serialized data of thread.
    """
    user, _ = validate_pin_unpin_thread_request_data(user_id, thread_id)
    pin_unpin_thread(thread_id, action)
    return get_pinned_unpinned_thread_serialized_data(user, thread_id)
