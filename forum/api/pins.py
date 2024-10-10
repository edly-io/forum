"""
Native Python Pins APIs.
"""

import logging
from typing import Any, Optional

from forum.backend import get_backend
from forum.serializers.thread import ThreadSerializer
from forum.utils import ForumV2RequestError

log = logging.getLogger(__name__)


def pin_unpin_thread(
    user_id: str,
    thread_id: str,
    action: str,
    course_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Helper method to Pin or Unpin a thread.
    Parameters:
        user_id (str): The ID of the requested User.
        thread_id (str): The ID of the thread to pin.
        action: (str): It's value can be "pin" or "unpin".
    Response:
        A response with the updated thread data.
    """
    backend = get_backend(course_id)()
    try:
        thread_data: dict[str, Any] = backend.handle_pin_unpin_thread_request(
            user_id, thread_id, action, ThreadSerializer
        )
    except ValueError as e:
        log.error(f"Forumv2RequestError for {action} thread request.")
        raise ForumV2RequestError(str(e)) from e

    return thread_data


def pin_thread(
    user_id: str, thread_id: str, course_id: Optional[str] = None
) -> dict[str, Any]:
    """
    Pin a thread.
    Parameters:
        user_id (str): The ID of the requested User.
        thread_id (str): The ID of the thread to pin.
    Response:
        A response with the updated thread data.
    """

    return pin_unpin_thread(user_id, thread_id, "pin", course_id)


def unpin_thread(
    user_id: str, thread_id: str, course_id: Optional[str] = None
) -> dict[str, Any]:
    """
    Unpin a thread.
    Parameters:
        user_id (str): The ID of the requested User.
        thread_id (str): The ID of the thread to pin.
    Response:
        A response with the updated thread data.
    """
    return pin_unpin_thread(user_id, thread_id, "unpin", course_id)
