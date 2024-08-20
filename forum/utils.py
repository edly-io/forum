"""Forum Utils."""

import logging

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
