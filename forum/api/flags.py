"""
This module contains the functions to update the flag status of a comment.
"""

from typing import Any, Optional

from forum.backends.mongodb.api import (
    flag_as_abuse,
    un_flag_all_as_abuse,
    un_flag_as_abuse,
)
from forum.backends.mongodb.comments import Comment
from forum.backends.mongodb.threads import CommentThread
from forum.backends.mongodb.users import Users
from forum.serializers.comment import CommentSerializer
from forum.serializers.thread import ThreadSerializer
from forum.utils import ForumV2RequestError


def update_comment_flag(
    comment_id: str,
    action: str,
    user_id: Optional[str] = None,
    update_all: Optional[bool] = False,
) -> dict[str, Any]:
    """
    Update the flag status of a comment.

    Args:
        user_id (str): The ID of the user.
        comment_id (str): The ID of the comment.
        action (str): The action to perform ("flag" or "unflag").
        update_all (bool, optional): Whether to update all flags. Defaults to False.
    """
    if not user_id:
        raise ForumV2RequestError("user_id not provided in params")
    user = Users().get(user_id)
    comment = Comment().get(comment_id)
    if not user or not comment:
        raise ForumV2RequestError("User / Comment doesn't exist")

    if action == "flag":
        updated_comment = flag_as_abuse(user, comment)
    elif action == "unflag":
        if update_all:
            updated_comment = un_flag_all_as_abuse(comment)
        else:
            updated_comment = un_flag_as_abuse(user, comment)
    else:
        raise ForumV2RequestError("Invalid action")

    if updated_comment is None:
        raise ForumV2RequestError("Failed to update comment")

    context = {
        "id": str(updated_comment["_id"]),
        **updated_comment,
        "user_id": user["_id"],
        "username": user["username"],
        "type": "comment",
        "thread_id": str(updated_comment.get("comment_thread_id", None)),
    }
    return CommentSerializer(context).data


def update_thread_flag(
    thread_id: str,
    action: str,
    user_id: Optional[str] = None,
    update_all: Optional[bool] = False,
) -> dict[str, Any]:
    """
    Update the flag status of a thread.

    Args:
        user_id (str): The ID of the user.
        thread_id (str): The ID of the thread.
        action (str): The action to perform ("flag" or "unflag").
        update_all (bool, optional): Whether to update all flags. Defaults to False.
    """
    if not user_id:
        raise ForumV2RequestError("user_id not provided in params")
    user = Users().get(user_id)
    thread = CommentThread().get(thread_id)
    if not user or not thread:
        raise ForumV2RequestError("User / Thread doesn't exist")

    if action == "flag":
        updated_thread = flag_as_abuse(user, thread)
    elif action == "unflag":
        if update_all:
            updated_thread = un_flag_all_as_abuse(thread)
        else:
            updated_thread = un_flag_as_abuse(user, thread)
    else:
        raise ForumV2RequestError("Invalid action")

    if updated_thread is None:
        raise ForumV2RequestError("Failed to update thread")

    context = {
        "id": str(updated_thread["_id"]),
        **updated_thread,
        "user_id": user["_id"],
        "username": user["username"],
        "type": "thread",
        "thread_id": str(updated_thread.get("comment_thread_id", None)),
    }
    return ThreadSerializer(context).data
