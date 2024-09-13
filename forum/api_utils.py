"""Forum Utils."""

import logging
from typing import Any

from forum.models.users import Users
from forum.models.model_utils import (
    get_group_ids_from_params,
    handle_pin_unpin_thread_request,
    user_to_hash,
)
from forum.serializers.thread import ThreadSerializer
from forum.serializers.users import UserSerializer
from forum.utils import ForumV2RequestError

log = logging.getLogger(__name__)


def pin_unpin_thread(
    user_id: str,
    thread_id: str,
    action: str,
) -> dict[str, Any]:
    """Pin or Unpin  a thread."""
    try:
        thread_data: dict[str, Any] = handle_pin_unpin_thread_request(
            user_id, thread_id, action, ThreadSerializer
        )
    except ValueError as e:
        log.error(f"Forumv2RequestError for {action} thread request.")
        raise ForumV2RequestError(str(e)) from e

    return thread_data


def retrieve_user_data(user_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """Get user data."""
    user = Users().get(user_id)
    if not user:
        log.error(f"Forumv2RequestError for retrieving user's data for id {user_id}.")
        raise ForumV2RequestError(str(f"user not found with id: {user_id}"))

    group_ids = get_group_ids_from_params(params)
    params.update({"group_ids": group_ids})
    hashed_user = user_to_hash(user, params)
    serializer = UserSerializer(hashed_user)
    return serializer.data
