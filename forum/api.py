"""
Native Python Functions.
"""

from typing import Any

from forum.models.model_utils import get_commentables_counts_based_on_type
from forum.views.pins import pin_unpin_thread
from forum.views.users import retrieve_user_data


def pin_thread(user_id: str, thread_id: str) -> dict[str, Any]:
    """Pin a thread."""
    return pin_unpin_thread(user_id, thread_id, "pin")


def retrieve_commentables_stats(course_id: str) -> dict[str, Any]:
    """Retrieve Commentables stats."""
    return get_commentables_counts_based_on_type(course_id)


def retrieve_user(
    user_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Get user data by user_id."""
    return retrieve_user_data(user_id, data)


def unpin_thread(user_id: str, thread_id: str) -> dict[str, Any]:
    """Unpin a thread."""
    return pin_unpin_thread(user_id, thread_id, "unpin")
