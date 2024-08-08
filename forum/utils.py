"""Forum Utils."""

import logging

import requests
from django.conf import settings

from forum.models.contents import Contents
from forum.models.users import Users


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


def flag_as_abuse(user, entity):
    """
    Flag an entity as abuse.

    Args:
        user (dict): The user who is flagging the entity as abuse.
        entity (dict): The entity being flagged as abuse.

    Returns:
        dict: The updated entity with the abuse flag.

    Raises:
        ValueError: If user ID or entity is not provided.
    """
    if not (user and entity):
        raise ValueError("User ID/Entity is required")
    # Check if user ID is already in abuse flaggers list
    abuse_flaggers = entity["abuse_flaggers"]
    if user["_id"] not in abuse_flaggers:
        abuse_flaggers.append(user["_id"])
        Contents().collection.update_one(
            {"_id": entity["_id"]},
            {"$set": {"abuse_flaggers": abuse_flaggers}},
        )

    # Check if this is the first abuse flag
    first_flag_added = len(entity["abuse_flaggers"]) == 1

    # If this is the first abuse flag, update author's stats
    if first_flag_added:
        Users().collection.update_one(
            {"_id": entity["author_id"]},
            {"$inc": {"active_flags": 1}},
        )

    # Reload the object and return it as a JSON string
    return Contents().get(_id=entity["_id"])


def un_flag_as_abuse(user, entity, _all=True):
    """
    Unflag an entity as abuse.

    Args:
        user (dict): The user who is unflagging the entity as abuse.
        entity (dict): The entity being unflagged as abuse.
        all (bool, optional): Whether to remove all abuse flags or just the current user's flag. Defaults to True.

    Returns:
        dict: The updated entity with the abuse flag removed.

    Raises:
        ValueError: If user ID or entity is not provided.
    """
    if not (user and entity):
        raise ValueError("User ID/Entity is required")
    if _all:
        Contents().collection.update_one(
            {"_id": entity.get("_id")}, {"$set": {"abuse_flaggers": []}},
        )
    else:
        if user["_id"] in entity["abuse_flaggers"]:
            entity["abuse_flaggers"].remove(user["_id"])
            Contents().collection.update_one(
                {"_id": entity["_id"]},
                {"$set": {"abuse_flaggers": entity["abuse_flaggers"]}},
            )
    # TODO: Update course stats for abuse.
    return Contents().get(_id=entity["_id"])
