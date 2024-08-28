"""Forum Utils."""

import logging
from typing import Any

import requests
from django.conf import settings
from django.http import HttpRequest
from requests.models import Response

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
        "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key", ""),
        "Accept-Language": request.headers.get("Accept-Language", ""),
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


def str_to_bool(value: str) -> bool:
    """Convert str to bool."""
    return value.lower() in ("true", "1")


def get_int_value_from_collection(
    collection: dict[str, Any], key: str, default_value: int
) -> int:
    """
    Get int value from the collection."""
    try:
        return int(collection[key])
    except (TypeError, ValueError, KeyError):
        return default_value


def prepare_comment_data_for_get_children(children):
    children_data = []
    for child in children:
        children_data.append(
            {
                **child,
                "id": str(child.get("_id")),
                "user_id": child.get("author_id"),
                "thread_id": str(child.get("comment_thread_id")),
                "username": child.get("author_username"),
                "parent_id": str(child.get("parent_id")),
                "type": str(child.get("_type", "")).lower(),
            }
        )
    return children_data
