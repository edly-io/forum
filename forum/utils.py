"""Forum Utils."""

import logging
from typing import Any

import requests
from django.conf import settings
from django.dispatch import Signal
from django.http import HttpRequest
from requests.models import Response

log = logging.getLogger(__name__)


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
    comments_service_url = getattr(
        settings, "CS_COMMENTS_SERVICE_URL", "http://forum:4567"
    )
    url = f"{comments_service_url}/api/v1/{suffix}"
    request_headers = {
        "X-Edx-Api-Key": request.headers.get("X-Edx-Api-Key", ""),
        "Accept-Language": request.headers.get("Accept-Language", ""),
    }
    request_data = request.POST.dict()
    request_params = request.GET.dict()

    log.error(
        "%s request to Forum V1 URL: %s with Params: %s and Data: %s",
        method.upper(),
        url,
        request_params,
        request_data,
    )
    return requests.request(
        method,
        url,
        data=request_data,
        params=request_params,
        headers=request_headers,
        timeout=5.0,
    )


def str_to_bool(value: str | bool) -> bool:
    """
    Convert a string or boolean value to a boolean.

    If the input is already a boolean, the value is returned as is.
    For string inputs, 'true' (case-insensitive) or '1' are considered True,
    while any other value is considered False.

    Args:
        value (str | bool): The input value, either a string or a boolean.

    Returns:
        bool: The converted boolean value.
    """
    if isinstance(value, bool):
        return value
    return value.lower() in ("true", "1")


def get_int_value_from_collection(
    collection: dict[str, Any], key: str, default_value: int
) -> int:
    """
    Get int value from the collection.
    """
    try:
        return int(collection[key])
    except (TypeError, ValueError, KeyError):
        return default_value


def get_str_value_from_collection(collection: dict[str, Any], key: str) -> str:
    """
    Get str value from the collection.
    """
    try:
        value = str(collection[key])
    except (TypeError, ValueError, KeyError) as exception:
        raise ValueError("Invalud Value") from exception
    return value


def get_handler_by_name(name: str) -> Signal:
    """
    Return the signal handler by name.

    Args:
        name (str): The name of the signal.

    Returns:
        Signal: The corresponding signal object.
    """
    # TODO: Remove this function when we shift to MySQL as we can receive the signals
    # directly from the model updates using pose_save and other methods.
    from forum import signals  # pylint: disable=cyclic-import import-outside-toplevel

    map_signals = {
        "comment_deleted": signals.comment_deleted,
        "comment_thread_deleted": signals.comment_thread_deleted,
        "comment_inserted": signals.comment_inserted,
        "comment_thread_inserted": signals.comment_thread_inserted,
        "comment_updated": signals.comment_updated,
        "comment_thread_updated": signals.comment_thread_updated,
    }

    try:
        return map_signals[name]
    except KeyError as exc:
        raise KeyError(f"No signal found for the name: {name}") from exc


def prepare_comment_data_for_get_children(
    children: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Prepare children data to be used in serializer."""
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
