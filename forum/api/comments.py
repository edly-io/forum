"""
Native Python Comments APIs.
"""

import logging
from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError

from forum.backends.mongodb import Comment, CommentThread, Users
from forum.backends.mongodb.api import (
    mark_as_read,
    validate_object,
    update_stats_for_course,
)
from forum.serializers.comment import CommentSerializer
from forum.utils import ForumV2RequestError, str_to_bool

log = logging.getLogger(__name__)


def validate_comments_request_data(data: dict[str, Any]) -> None:
    """
    Validates the request data if it exists or not.

    Parameters:
        data: request data to validate.
    Response:
        raise exception if some data does not exists.
    """
    fields_to_validate = ["body", "course_id", "user_id"]
    for field in fields_to_validate:
        if field not in data or not data[field]:
            raise ValueError(f"{field} is missing.")


def create_comment(
    data: dict[str, Any],
    depth: int,
    thread_id: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> Any:
    """handle comment creation and returns a comment"""
    author_id = data["user_id"]
    course_id = data["course_id"]
    new_comment_id = Comment().insert(
        body=data["body"],
        course_id=course_id,
        anonymous=str_to_bool(data.get("anonymous", "False")),
        anonymous_to_peers=str_to_bool(data.get("anonymous_to_peers", "False")),
        author_id=author_id,
        comment_thread_id=thread_id,
        parent_id=parent_id,
        depth=depth,
    )
    if parent_id:
        update_stats_for_course(author_id, course_id, replies=1)
    else:
        update_stats_for_course(author_id, course_id, responses=1)
    return Comment().get(new_comment_id)


def prepare_comment_api_response(
    comment: dict[str, Any],
    exclude_fields: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Return serialized validated data.

    Parameters:
        comment: The comment details that needs to be serialized.
        exclude_fields: Any fields that need to be excluded from response.

    Response:
        serialized validated data of the comment.
    """
    comment_data = {
        **comment,
        "id": str(comment.get("_id")),
        "user_id": comment.get("author_id"),
        "thread_id": str(comment.get("comment_thread_id")),
        "username": comment.get("author_username"),
        "parent_id": str(comment.get("parent_id")),
        "type": str(comment.get("_type", "")).lower(),
    }
    if not exclude_fields:
        exclude_fields = []
    exclude_fields.append("children")
    serializer = CommentSerializer(
        data=comment_data,
        exclude_fields=exclude_fields,
    )
    if not serializer.is_valid(raise_exception=True):
        raise ValidationError(serializer.errors)

    return serializer.data


def get_update_comment_data(data: dict[str, str | bool]) -> dict[str, str | bool]:
    """convert request data to a dict excluding empty data"""

    fields = [
        ("body", data.get("body")),
        ("course_id", data.get("course_id")),
        ("anonymous", str_to_bool(data.get("anonymous", "False"))),
        (
            "anonymous_to_peers",
            str_to_bool(data.get("anonymous_to_peers", "False")),
        ),
        ("closed", str_to_bool(data.get("closed", "False"))),
        ("endorsed", str_to_bool(data.get("endorsed", "False"))),
        ("author_id", data.get("user_id")),
        ("editing_user_id", data.get("editing_user_id")),
        ("edit_reason_code", data.get("edit_reason_code")),
        ("endorsement_user_id", data.get("endorsement_user_id")),
    ]
    return {field: value for field, value in fields if value is not None}


def get_parent_comment(comment_id: str) -> dict[str, Any]:
    """
    Get a parent comment.

    Parameters:
        comment_id: The ID of the comment.
    Body:
        Empty.
    Response:
        The details of the comment for the given comment_id.
    """
    try:
        comment = validate_object(Comment, comment_id)
    except ObjectDoesNotExist as exc:
        log.error("Forumv2RequestError for get parent comment request.")
        raise ForumV2RequestError(
            f"Comment does not exists with Id: {comment_id}"
        ) from exc
    return prepare_comment_api_response(
        comment,
        exclude_fields=["sk"],
    )


def create_child_comment(
    parent_comment_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    """
    Create a new child comment.

    Parameters:
        comment_id: The ID of the parent comment for creating it's child comment.
    Body:
        body: The content of the comment.
        course_id: The Id of the respective course.
        user_id: The requesting user id.
        anonymous: anonymous flag(True or False).
        anonymous_to_peers: anonymous to peers flag(True or False).
    Response:
        The details of the comment that is created.
    """
    try:
        parent_comment = validate_object(Comment, parent_comment_id)
    except ObjectDoesNotExist as exc:
        log.error("Forumv2RequestError for create child comment request.")
        raise ForumV2RequestError(
            f"Comment does not exists with Id: {parent_comment_id}"
        ) from exc
    try:
        validate_comments_request_data(data)
    except ValueError as error:
        log.error("Forumv2RequestError for create child comment request.")
        raise error

    comment = create_comment(data, 1, parent_id=parent_comment_id)
    if not comment:
        log.error("Forumv2RequestError for create child comment request.")
        raise ForumV2RequestError("comment is not created")

    user = Users().get(data["user_id"])
    thread = CommentThread().get(parent_comment["comment_thread_id"])
    if user and thread and comment:
        mark_as_read(user, thread)
    try:
        comment_data = prepare_comment_api_response(
            comment,
            exclude_fields=["endorsement", "sk"],
        )
        return comment_data
    except ValidationError as error:
        raise error


def update_comment(
    comment_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Update an existing child/parent comment.

    Parameters:
        comment_id: The ID of the comment to be edited.
    Body:
        fields to be updated.
    Response:
        The details of the comment that is updated.
    """
    try:
        comment = validate_object(Comment, comment_id)
    except ObjectDoesNotExist as exc:
        log.error("Forumv2RequestError for update comment request.")
        raise ForumV2RequestError(
            f"Comment does not exists with Id: {comment_id}"
        ) from exc

    update_comment_data: dict[str, Any] = get_update_comment_data(data)
    if comment:
        update_comment_data["edit_history"] = comment.get("edit_history", [])
        update_comment_data["original_body"] = comment.get("body")

    Comment().update(comment_id, **update_comment_data)
    updated_comment = Comment().get(comment_id)
    if not updated_comment:
        log.error("Forumv2RequestError for create child comment request.")
        raise ForumV2RequestError("comment is not updated")
    try:
        return prepare_comment_api_response(
            updated_comment,
            exclude_fields=(
                ["endorsement", "sk"] if updated_comment.get("parent_id") else ["sk"]
            ),
        )
    except ValidationError as error:
        raise error


def delete_comment(comment_id: str) -> dict[str, Any]:
    """
    Delete a comment.

    Parameters:
        comment_id: The ID of the comment to be deleted.
    Body:
        Empty.
    Response:
        The details of the comment that is deleted.
    """
    try:
        comment = validate_object(Comment, comment_id)
    except ObjectDoesNotExist as exc:
        log.error("Forumv2RequestError for delete comment request.")
        raise ForumV2RequestError(
            f"Comment does not exists with Id: {comment_id}"
        ) from exc
    data = prepare_comment_api_response(
        comment,
        exclude_fields=["endorsement", "sk"],
    )
    Comment().delete(comment_id)
    author_id = comment["author_id"]
    course_id = comment["course_id"]
    parent_comment_id = data["parent_id"]
    if parent_comment_id:
        update_stats_for_course(author_id, course_id, replies=-1)
    else:
        update_stats_for_course(author_id, course_id, responses=-1)
    return data


def create_parent_comment(thread_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new parent comment.

    Parameters:
        thread_id: The ID of the thread for creating a comment on it.
    Body:
        body: The content of the comment.
        course_id: The Id of the respective course.
        user_id: The requesting user id.
        anonymous: anonymous flag(True or False).
        anonymous_to_peers: anonymous to peers flag(True or False).
    Response:
        The details of the comment that is created.
    """
    try:
        thread = validate_object(CommentThread, thread_id)
    except ObjectDoesNotExist as exc:
        log.error("Forumv2RequestError for create parent comment request.")
        raise ForumV2RequestError(
            f"Thread does not exists with Id: {thread_id}"
        ) from exc
    try:
        validate_comments_request_data(data)
    except ValueError as error:
        log.error("Forumv2RequestError for create parent comment request.")
        raise error

    comment = create_comment(data, 0, thread_id=thread_id)
    if not comment:
        log.error("Forumv2RequestError for create parent comment request.")
        raise ForumV2RequestError("comment is not created")
    user = Users().get(data["user_id"])
    if user and comment:
        mark_as_read(user, thread)
    try:
        return prepare_comment_api_response(
            comment,
            exclude_fields=["endorsement", "sk"],
        )
    except ValidationError as error:
        raise error
