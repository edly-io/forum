"""Forum Utils."""

import logging

import requests
from django.conf import settings

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
