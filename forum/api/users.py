"""
Native Python Users APIs.
"""

import logging
from typing import Any

from forum.backends.mongodb import Users
from forum.backends.mongodb.api import (
    get_group_ids_from_params,
    user_to_hash,
)
from forum.serializers.users import UserSerializer
from forum.utils import ForumV2RequestError

log = logging.getLogger(__name__)


def get_user(user_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """Get user data by user_id."""
    """
    Get users data by user_id.
    Parameters:
        user_id (str): The ID of the requested User.
        params (str): attributes for user's data filteration.
    Response:
        A response with the users data.
    """
    user = Users().get(user_id)
    if not user:
        log.error(f"Forumv2RequestError for retrieving user's data for id {user_id}.")
        raise ForumV2RequestError(str(f"user not found with id: {user_id}"))

    group_ids = get_group_ids_from_params(params)
    params.update({"group_ids": group_ids})
    hashed_user = user_to_hash(user, params)
    serializer = UserSerializer(hashed_user)
    return serializer.data
