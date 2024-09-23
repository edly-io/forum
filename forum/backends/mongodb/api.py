"""Model util function for db operations."""

import math
from datetime import datetime, timezone
from typing import Any, Optional, Union

from bson import ObjectId
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from forum.backends.mongodb import (
    Comment,
    CommentThread,
    Contents,
    Subscriptions,
    Users,
)
from forum.constants import RETIRED_BODY, RETIRED_TITLE
from forum.utils import get_group_ids_from_params, get_sort_criteria, make_aware


def update_stats_for_course(user_id: str, course_id: str, **kwargs: Any) -> None:
    """Update stats for a course."""
    user = Users().get(user_id)
    if not user:
        raise ObjectDoesNotExist
    course_stats = user.get("course_stats", [])
    for course_stat in course_stats:
        if course_stat["course_id"] == course_id:
            course_stat.update(
                {k: course_stat[k] + v for k, v in kwargs.items() if k in course_stat}
            )
            Users().update(
                user_id,
                course_stats=course_stats,
            )
            return
    build_course_stats(user["_id"], course_id)


def flag_as_abuse(
    user: dict[str, Any], entity: dict[str, Any]
) -> Union[dict[str, Any], None]:
    """
    Flag an entity as abuse.

    Args:
        user (dict[str, Any]): The user who is flagging the entity as abuse.
        entity (dict[str, Any]): The entity being flagged as abuse.

    Returns:
        dict[str, Any]: The updated entity with the abuse flag.

    Raises:
        ValueError: If user ID or entity is not provided.
    """

    abuse_flaggers = entity["abuse_flaggers"]
    first_flag_added = False
    if user["_id"] not in abuse_flaggers:
        abuse_flaggers.append(user["_id"])
        first_flag_added = len(abuse_flaggers) == 1
        Contents().update(
            entity["_id"],
            abuse_flaggers=abuse_flaggers,
        )
    if first_flag_added:
        update_stats_for_course(
            entity["author_id"],
            entity["course_id"],
            active_flags=1,
        )
    return Contents().get(entity["_id"])


def update_stats_after_unflag(
    user_id: str, entity_id: str, has_no_historical_flags: bool
) -> None:
    """Update the stats for the course after unflagging an entity."""
    entity = Contents().get(entity_id)
    if not entity:
        raise ObjectDoesNotExist

    first_historical_flag = (
        has_no_historical_flags and not entity["historical_abuse_flaggers"]
    )
    if first_historical_flag:
        update_stats_for_course(user_id, entity["course_id"], inactive_flags=1)

    if not entity["abuse_flaggers"]:
        update_stats_for_course(user_id, entity["course_id"], active_flags=-1)


def un_flag_as_abuse(
    user: dict[str, Any], entity: dict[str, Any]
) -> Union[dict[str, Any], None]:
    """
    Unflag an entity as abuse.

    Args:
        user (dict[str, Any]): The user who is unflagging the entity as abuse.
        entity (dict[str, Any]): The entity being unflagged as abuse.

    Returns:
        dict[str, Any]: The updated entity with the abuse flag removed.

    Raises:
        ValueError: If user ID or entity is not provided.
    """
    has_no_historical_flags = len(entity["historical_abuse_flaggers"]) == 0
    if user["_id"] in entity["abuse_flaggers"]:
        entity["abuse_flaggers"].remove(user["_id"])
        Contents().update(
            entity["_id"],
            abuse_flaggers=entity["abuse_flaggers"],
        )
        update_stats_after_unflag(
            entity["author_id"], entity["_id"], has_no_historical_flags
        )

    return Contents().get(entity["_id"])


def un_flag_all_as_abuse(entity: dict[str, Any]) -> Union[dict[str, Any], None]:
    """
    Unflag an entity as abuse for all users.

    Args:
        entity (dict[str, Any]): The entity being unflagged as abuse.

    Returns:
        dict[str, Any]: The updated entity with all abuse flags removed.

    Raises:
        ValueError: If entity is not provided.
    """
    has_no_historical_flags = len(entity["historical_abuse_flaggers"]) == 0
    historical_abuse_flaggers = list(
        set(entity["historical_abuse_flaggers"]) | set(entity["abuse_flaggers"])
    )
    Contents().update(
        entity["_id"],
        abuse_flaggers=[],
        historical_abuse_flaggers=historical_abuse_flaggers,
    )
    update_stats_after_unflag(
        entity["author_id"], entity["_id"], has_no_historical_flags
    )

    return Contents().get(entity["_id"])


def update_vote(
    content: dict[str, Any],
    user: dict[str, Any],
    vote_type: str = "",
    is_deleted: bool = False,
) -> bool:
    """
    Update a vote on a thread (either upvote or downvote).

    :param content: The content document containing vote data.
    :param user: The user document for the user voting.
    :param vote_type: String indicating the type of vote ('up' or 'down').
    :param is_deleted: Boolean indicating if the user is removing their vote (True) or voting (False).
    :return: True if the vote was successfully updated, False otherwise.
    """
    user_id: str = user["_id"]
    content_id: str = str(content["_id"])
    votes: dict[str, Any] = content["votes"]

    update_needed: bool = False

    if not is_deleted:
        if vote_type not in ["up", "down"]:
            raise ValueError("Invalid vote_type, use ('up' or 'down')")

        if vote_type == "up":
            current_votes = set(votes["up"])
            opposite_votes = set(votes["down"])
        else:
            current_votes = set(votes["down"])
            opposite_votes = set(votes["up"])

        # Check if user is voting
        if user_id not in current_votes:
            current_votes.add(user_id)
            update_needed = True
            if user_id in opposite_votes:
                opposite_votes.remove(user_id)

        updated_up_votes = opposite_votes if vote_type == "down" else current_votes
        updated_down_votes = current_votes if vote_type == "down" else opposite_votes

    else:
        # Handle vote deletion
        updated_up_votes = set(votes["up"])
        updated_down_votes = set(votes["down"])

        if user_id in updated_up_votes:
            updated_up_votes.remove(user_id)
            update_needed = True
        if user_id in updated_down_votes:
            updated_down_votes.remove(user_id)
            update_needed = True

    if update_needed:
        # Prepare updated votes
        content_model = Contents()
        updated_votes = content_model.get_votes_dict(
            list(updated_up_votes), list(updated_down_votes)
        )
        updated_count = content_model.update_votes(
            content_id=content_id, votes=updated_votes
        )
        return bool(updated_count)

    return False


def upvote_content(thread: dict[str, Any], user: dict[str, Any]) -> bool:
    """
    Upvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be upvoted.
        user (dict): The user who is performing the upvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(thread, user, vote_type="up")


def downvote_content(thread: dict[str, Any], user: dict[str, Any]) -> bool:
    """
    Downvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be downvoted.
        user (dict): The user who is performing the downvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(thread, user, vote_type="down")


def remove_vote(thread: dict[str, Any], user: dict[str, Any]) -> bool:
    """
    Remove the vote (upvote or downvote) from the specified thread or comment for the given user.

    Args:
        thread (dict): The thread or comment data from which the vote should be removed.
        user (dict): The user who is removing their vote.

    Returns:
        bool: True if the vote was successfully removed, False otherwise.
    """
    return update_vote(thread, user, is_deleted=True)


def validate_thread_and_user(
    user_id: str, thread_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Validate thread and user.

    Arguments:
        user_id (str): The ID of the user making the request.
        thread_id (str): The ID of the thread.

    Returns:
        tuple[dict[str, Any], dict[str, Any]]: A tuple containing the user and thread data.

    Raises:
        ValueError: If the thread or user is not found.
    """
    thread = CommentThread().get(thread_id)
    user = Users().get(user_id)
    if not (thread and user):
        raise ValueError("User / Thread doesn't exist")

    return user, thread


def pin_unpin_thread(thread_id: str, action: str) -> None:
    """
    Pin or unpin the thread based on action parameter.

    Arguments:
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").
    """
    CommentThread().update(thread_id, pinned=action == "pin")


def get_pinned_unpinned_thread_serialized_data(
    user: dict[str, Any], thread_id: str, serializer_class: Any
) -> dict[str, Any]:
    """
    Return serialized data of pinned or unpinned thread.

    Arguments:
        user (dict[str, Any]): The user who requested the action.
        thread_id (str): The ID of the thread to pin/unpin.

    Returns:
        dict[str, Any]: The serialized data of the pinned/unpinned thread.

    Raises:
        ValueError: If the serialization is not valid.
    """
    updated_thread = CommentThread().get(thread_id)
    context = {
        "user_id": user["_id"],
        "username": user["username"],
        "type": "thread",
        "id": thread_id,
    }
    if updated_thread is not None:
        context = {**context, **updated_thread}
    serializer = serializer_class(data=context)
    if not serializer.is_valid():
        raise ValueError(serializer.errors)

    return serializer.data


def handle_pin_unpin_thread_request(
    user_id: str, thread_id: str, action: str, serializer_class: Any
) -> dict[str, Any]:
    """
    Catches pin/unpin thread request.

    - validates thread and user.
    - pin or unpin the thread based on action parameter.
    - return serialized data of thread.

    Arguments:
        user_id (str): The ID of the user making the request.
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").

    Returns:
        dict[str, Any]: The serialized data of the pinned/unpinned thread.
    """
    user, _ = validate_thread_and_user(user_id, thread_id)
    pin_unpin_thread(thread_id, action)
    return get_pinned_unpinned_thread_serialized_data(user, thread_id, serializer_class)


def get_abuse_flagged_count(thread_ids: list[str]) -> dict[str, int]:
    """
    Retrieves the count of abuse-flagged comments for each thread in the provided list of thread IDs.

    Args:
        thread_ids (list[str]): List of thread IDs to check for abuse flags.

    Returns:
        dict[str, int]: A dictionary mapping thread IDs to their corresponding abuse-flagged comment count.
    """
    pipeline: list[dict[str, Any]] = [
        {
            "$match": {
                "comment_thread_id": {"$in": [ObjectId(tid) for tid in thread_ids]},
                "abuse_flaggers": {"$ne": []},
            }
        },
        {"$group": {"_id": "$comment_thread_id", "flagged_count": {"$sum": 1}}},
    ]
    flagged_threads = Contents().aggregate(pipeline)

    return {str(item["_id"]): item["flagged_count"] for item in flagged_threads}


def get_read_states(
    threads: list[dict[str, Any]], user_id: str, course_id: str
) -> dict[str, list[Any]]:
    """
    Retrieves the read state and unread comment count for each thread in the provided list.

    Args:
        threads (list[dict[str, Any]]): list of threads to check read state for.
        user_id (str): The ID of the user whose read states are being retrieved.
        course_id (str): The course ID associated with the threads.

    Returns:
        dict[str, list[Any]]: A dictionary mapping thread IDs to a list containing
        whether the thread is read and the unread comment count.
    """
    read_states = {}
    if user_id:
        user = Users().find_one({"_id": user_id, "read_states.course_id": course_id})
        read_state = user["read_states"][0] if user else {}
        if read_state:
            read_dates = read_state.get("last_read_times", {})
            for thread in threads:
                thread_key = str(thread["_id"])
                if thread_key in read_dates:
                    read_date = make_aware(read_dates[thread_key])
                    last_activity_at = make_aware(thread["last_activity_at"])
                    is_read = read_date >= last_activity_at
                    unread_comment_count = Contents().count_documents(
                        {
                            "comment_thread_id": ObjectId(thread_key),
                            "created_at": {"$gte": read_dates[thread_key]},
                            "author_id": {"$ne": str(user_id)},
                        }
                    )
                    read_states[thread_key] = [is_read, unread_comment_count]

    return read_states


def get_endorsed(thread_ids: list[str]) -> dict[str, bool]:
    """
    Retrieves endorsed status for each thread in the provided list of thread IDs.

    Args:
        thread_ids (list[str]): List of thread IDs to check for endorsement.

    Returns:
        dict[str, bool]: A dictionary mapping thread IDs to their endorsed status (True if endorsed, False otherwise).
    """
    endorsed_comments = Comment().find(
        {
            "comment_thread_id": {"$in": [ObjectId(tid) for tid in thread_ids]},
            "endorsed": True,
        }
    )

    return {str(item["comment_thread_id"]): True for item in endorsed_comments}


def get_user_read_state_by_course_id(
    user: dict[str, Any], course_id: str
) -> dict[str, Any]:
    """
    Retrieves the user's read state for a specific course.

    Args:
        user (dict[str, Any]): The user object containing read states.
        course_id (str): The course ID to filter the user's read state by.

    Returns:
        dict[str, Any]: The user's read state for the specified course, or an empty dictionary if not found.
    """
    for read_state in user.get("read_states", []):
        if read_state["course_id"] == course_id:
            return read_state
    return {}


# TODO: Make this function modular
# pylint: disable=too-many-nested-blocks,too-many-statements
def handle_threads_query(
    comment_thread_ids: list[str],
    user_id: str,
    course_id: str,
    group_ids: list[int],
    author_id: Optional[str],
    thread_type: Optional[str],
    filter_flagged: bool,
    filter_unread: bool,
    filter_unanswered: bool,
    filter_unresponded: bool,
    count_flagged: bool,
    sort_key: str,
    page: int,
    per_page: int,
    context: str = "course",
    raw_query: bool = False,
) -> dict[str, Any]:
    """
    Handles complex thread queries based on various filters and returns paginated results.

    Args:
        comment_thread_ids (list[str]): List of comment thread IDs to filter.
        user_id (str): The ID of the user making the request.
        course_id (str): The course ID associated with the threads.
        group_ids (list[int]): List of group IDs for group-based filtering.
        author_id (str): The ID of the author to filter threads by.
        thread_type (str): The type of thread to filter by.
        filter_flagged (bool): Whether to filter threads flagged for abuse.
        filter_unread (bool): Whether to filter unread threads.
        filter_unanswered (bool): Whether to filter unanswered questions.
        filter_unresponded (bool): Whether to filter threads with no responses.
        count_flagged (bool): Whether to include flagged content count.
        sort_key (str): The key to sort the threads by.
        page (int): The page number for pagination.
        per_page (int): The number of threads per page.
        context (str): The context to filter threads by.
        raw_query (bool): Whether to return raw query results without further processing.

    Returns:
        dict[str, Any]: A dictionary containing the paginated thread results and associated metadata.
    """
    # Convert thread_ids to ObjectId
    comment_thread_obj_ids: list[ObjectId] = [
        ObjectId(tid) for tid in comment_thread_ids
    ]

    # Base query
    base_query: dict[str, Any] = {
        "_id": {"$in": comment_thread_obj_ids},
        "context": context,
    }

    # Group filtering
    if group_ids:
        base_query["$or"] = [
            {"group_id": {"$in": group_ids}},
            {"group_id": {"$exists": False}},
        ]

    # Author filtering
    if author_id:
        base_query["author_id"] = author_id
        if author_id != user_id:
            base_query["anonymous"] = False
            base_query["anonymous_to_peers"] = False

    # Thread type filtering
    if thread_type:
        base_query["thread_type"] = thread_type

    # Flagged content filtering
    if filter_flagged:
        flagged_query = {
            "course_id": course_id,
            "abuse_flaggers": {"$ne": [], "$exists": True},
        }
        flagged_comments = Comment().distinct("comment_thread_id", flagged_query)
        flagged_threads = CommentThread().distinct("_id", flagged_query)
        base_query["_id"]["$in"] = list(
            set(comment_thread_obj_ids) & set(flagged_comments + flagged_threads)
        )

    # Unanswered questions filtering
    if filter_unanswered:
        endorsed_threads = Comment().distinct(
            "comment_thread_id",
            {"course_id": course_id, "parent_id": {"$exists": False}, "endorsed": True},
        )
        base_query["thread_type"] = "question"
        base_query["_id"]["$nin"] = endorsed_threads

    # Unresponded threads filtering
    if filter_unresponded:
        base_query["comment_count"] = 0

    sort_criteria = get_sort_criteria(sort_key)

    comment_threads = CommentThread().find(base_query)
    thread_count = CommentThread().count_documents(base_query)

    if sort_criteria or raw_query:
        request_user = Users().get(_id=user_id) if user_id else None

        if not raw_query:
            comment_threads = comment_threads.sort(sort_criteria)

        if filter_unread and request_user:
            read_state = get_user_read_state_by_course_id(request_user, course_id)
            read_dates = read_state.get("last_read_times", {})

            threads = []
            skipped = 0
            to_skip = (page - 1) * per_page
            has_more = False
            batch_size = 100

            for thread in comment_threads.batch_size(batch_size):
                thread_key = str(thread["_id"])
                if (
                    thread_key not in read_dates
                    or read_dates[thread_key] < thread["last_activity_at"]
                ):
                    if raw_query:
                        threads.append(thread)
                    elif skipped >= to_skip:
                        if len(threads) == per_page:
                            has_more = True
                            break
                        threads.append(thread)
                    else:
                        skipped += 1
            num_pages = page + 1 if has_more else page
        else:
            if raw_query:
                threads = list(comment_threads)
            else:
                page = max(1, page)
                paginated_collection = comment_threads.skip(
                    (page - 1) * per_page
                ).limit(per_page)
                threads = list(paginated_collection)
                num_pages = max(1, math.ceil(thread_count / per_page))

        if raw_query:
            return {"result": threads}
        if len(threads) == 0:
            collection = []
        else:
            collection = threads_presentor(threads, user_id, course_id, count_flagged)

        return {
            "collection": collection,
            "num_pages": num_pages,
            "page": page,
            "thread_count": thread_count,
        }

    return {}


def prepare_thread(
    thread: dict[str, Any],
    is_read: bool,
    unread_count: int,
    is_endorsed: bool,
    abuse_flagged_count: int,
) -> dict[str, Any]:
    """
    Prepares thread data for presentation.

    Args:
        thread (dict[str, Any]): The thread data.
        is_read (bool): Whether the thread is read.
        unread_count (int): The count of unread comments.
        is_endorsed (bool): Whether the thread is endorsed.
        abuse_flagged_count (int): The abuse flagged count.

    Returns:
        dict[str, Any]: A dictionary representing the prepared thread data.
    """
    return {
        "id": str(thread["_id"]),
        **thread,
        "type": "thread",
        "read": is_read,
        "unread_comments_count": unread_count,
        "endorsed": is_endorsed,
        "abuse_flagged_count": abuse_flagged_count,
    }


def threads_presentor(
    threads: list[dict[str, Any]],
    user_id: str,
    course_id: str,
    count_flagged: bool = False,
) -> list[dict[str, Any]]:
    """
    Presents the threads by preparing them for display.

    Args:
        threads (list[dict[str, Any]]): List of threads to present.
        user_id (str): The ID of the user presenting the threads.
        course_id (str): The course ID associated with the threads.
        count_flagged (bool, optional): Whether to include flagged content count. Defaults to False.

    Returns:
        list[dict[str, Any]]: A list of prepared thread data.
    """
    thread_ids = [str(thread["_id"]) for thread in threads]
    read_states = get_read_states(threads, user_id, course_id)
    threads_endorsed = get_endorsed(thread_ids)
    threads_flagged = get_abuse_flagged_count(thread_ids) if count_flagged else {}

    presenters = []
    for thread in threads:
        thread_key = str(thread["_id"])
        is_read, unread_count = read_states.get(
            thread_key, (False, thread["comment_count"])
        )
        is_endorsed = threads_endorsed.get(thread_key, False)
        abuse_flagged_count = threads_flagged.get(thread_key, 0)
        presenters.append(
            prepare_thread(
                thread,
                is_read,
                unread_count,
                is_endorsed,
                abuse_flagged_count,
            )
        )

    return presenters


def get_username_from_id(user_id: str) -> Optional[str]:
    """
    Retrieve the username associated with a given user ID.

    Args:
        _id (int): The unique identifier of the user.

    Returns:
        Optional[str]: The username of the user if found, or None if not.

    """
    user = Users().get(_id=user_id) or {}
    if username := user.get("username"):
        return username
    return None


def validate_object(model: Any, obj_id: str) -> Any:
    """
    Validates the object if it exists or not.

    Parameters:
        model: The model for which to validate the id.
        id: The ID of the object to validate in the model.
    Response:
        raise exception if object does not exists.
        return object
    """
    instance = model().get(obj_id)
    if not instance:
        raise ObjectDoesNotExist
    return instance


def find_subscribed_threads(user_id: str, course_id: Optional[str] = None) -> list[str]:
    """
    Find threads that a user is subscribed to in a specific course.

    Args:
        user_id (str): The ID of the user.
        course_id (str): The ID of the course.

    Returns:
        list: A list of thread ids that the user is subscribed to in the course.
    """
    subscriptions = Subscriptions()
    threads = CommentThread()

    subscription_filter = {"subscriber_id": user_id}
    subscriptions_cursor = subscriptions.find(subscription_filter)

    thread_ids = []
    for subscription in subscriptions_cursor:
        thread_ids.append(ObjectId(subscription["source_id"]))

    thread_filter: dict[str, Any] = {"_id": {"$in": thread_ids}}
    if course_id:
        thread_filter["course_id"] = course_id
    threads_cursor = threads.find(thread_filter)

    subscribed_ids = []
    for thread in threads_cursor:
        subscribed_ids.append(thread["_id"])

    return subscribed_ids


def subscribe_user(
    user_id: str, source_id: str, source_type: str
) -> dict[str, Any] | None:
    """Subscribe a user to a source."""
    subscription = Subscriptions().get_subscription(user_id, source_id)
    if not subscription:
        Subscriptions().insert(user_id, source_id, source_type)
        subscription = Subscriptions().get_subscription(user_id, source_id)
    return subscription


def unsubscribe_user(user_id: str, source_id: str) -> None:
    """Unsubscribe a user from a source."""
    Subscriptions().delete_subscription(user_id, source_id)


def delete_comments_of_a_thread(thread_id: str) -> None:
    """Delete comments of a thread."""
    for comment in Comment().get_list(
        comment_thread_id=ObjectId(thread_id),
        depth=0,
        parent_id=None,
    ):
        Comment().delete(comment["_id"])


def delete_subscriptions_of_a_thread(thread_id: str) -> None:
    """Delete subscriptions of a thread."""
    for subscription in Subscriptions().get_list(
        source_id=thread_id, source_type="CommentThread"
    ):
        Subscriptions().delete_subscription(
            subscription["subscriber_id"], subscription["source_id"]
        )


def validate_params(
    params: dict[str, Any], user_id: Optional[str] = None
) -> Response | None:
    """
    Validate the request parameters.

    Args:
        params (dict): The request parameters.
        user_id (optional[str]): The Id of the user for validation.

    Returns:
        Response: A Response object with an error message if doesn't exist.
    """
    valid_params = [
        "course_id",
        "author_id",
        "thread_type",
        "flagged",
        "unread",
        "unanswered",
        "unresponded",
        "count_flagged",
        "sort_key",
        "page",
        "per_page",
        "request_id",
        "commentable_ids",
    ]
    if not user_id:
        valid_params.append("user_id")
        user_id = params.get("user_id")

    for key in params:
        if key not in valid_params:
            return Response(
                {"error": f"Invalid parameter: {key}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if "course_id" not in params:
        return Response(
            {"error": "Missing required parameter: course_id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_id:
        user = Users().get(user_id)
        if not user:
            return Response(
                {"error": "User doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return None


def get_threads(
    params: dict[str, Any],
    user_id: str,
    serializer: Any,
    thread_ids: list[str],
) -> dict[str, Any]:
    """get subscribed or all threads of a specific course for a specific user."""
    count_flagged = bool(params.get("count_flagged", False))
    threads = handle_threads_query(
        thread_ids,
        user_id,
        params["course_id"],
        get_group_ids_from_params(params),
        params.get("author_id", ""),
        params.get("thread_type"),
        bool(params.get("flagged", False)),
        bool(params.get("unread", False)),
        bool(params.get("unanswered", False)),
        bool(params.get("unresponded", False)),
        count_flagged,
        params.get("sort_key", ""),
        int(params.get("page", 1)),
        int(params.get("per_page", 100)),
    )
    context: dict[str, Any] = {
        "count_flagged": count_flagged,
        "include_endorsed": True,
        "include_read_state": True,
    }
    if user_id:
        context["user_id"] = user_id
    serializer = serializer(threads.pop("collection"), many=True, context=context)
    threads["collection"] = serializer.data
    return threads


def get_commentables_counts_based_on_type(course_id: str) -> dict[str, Any]:
    """Return commentables counts in a course based on thread's type."""
    pipeline: list[dict[str, Any]] = [
        {"$match": {"course_id": course_id, "_type": "CommentThread"}},
        {
            "$group": {
                "_id": {"topic_id": "$commentable_id", "type": "$thread_type"},
                "count": {"$sum": 1},
            }
        },
    ]

    result = CommentThread().aggregate(pipeline)
    commentable_counts = {}
    for commentable in result:
        topic_id = commentable["_id"]["topic_id"]
        if topic_id not in commentable_counts:
            commentable_counts[topic_id] = {"discussion": 0, "question": 0}
        commentable_counts[topic_id].update(
            {commentable["_id"]["type"]: commentable["count"]}
        )

    return commentable_counts


def get_user_voted_ids(user_id: str, vote: str) -> list[str]:
    """Get the IDs of the posts voted by a user."""
    if vote not in ["up", "down"]:
        raise ValueError("Invalid vote type")

    content_model = Contents()
    contents = content_model.get_list()
    voted_ids = []
    for content in contents:
        votes = content["votes"][vote]
        if user_id in votes:
            voted_ids.append(content["_id"])

    return voted_ids


def filter_standalone_threads(comments: list[dict[str, Any]]) -> list[str]:
    """Filter out standalone threads from the list of threads."""
    filtered_comments = []
    for comment in comments:
        if not comment["context"] == "standalone":
            filtered_comments.append(comment)
    return [str([comment["comment_thread_id"]]) for comment in filtered_comments]


def user_to_hash(
    user: dict[str, Any], params: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Converts user data to a hash
    """
    if params is None:
        params = {}

    hash_data = {}
    hash_data["username"] = user["username"]
    hash_data["external_id"] = user["external_id"]

    comment_model = Comment()
    thread_model = CommentThread()

    if params.get("complete"):
        subscribed_thread_ids = find_subscribed_threads(user["external_id"])
        upvoted_ids = get_user_voted_ids(user["external_id"], "up")
        downvoted_ids = get_user_voted_ids(user["external_id"], "down")
        hash_data.update(
            {
                "subscribed_thread_ids": subscribed_thread_ids,
                "subscribed_commentable_ids": [],
                "subscribed_user_ids": [],
                "follower_ids": [],
                "id": user["external_id"],
                "upvoted_ids": upvoted_ids,
                "downvoted_ids": downvoted_ids,
                "default_sort_key": user["default_sort_key"],
            }
        )

    if params.get("course_id"):
        threads = thread_model.find(
            {
                "author_id": user["external_id"],
                "course_id": params["course_id"],
                "anonymous": False,
                "anonymouse_to_peers": False,
            }
        )
        comments = comment_model.find(
            {
                "author_id": user["external_id"],
                "course_id": params["course_id"],
                "anonymous": False,
                "anonymouse_to_peers": False,
            }
        )
        if params.get("group_ids"):
            specified_groups_or_global = params["group_ids"] + [None]
            group_query = {
                "_id": {"$in": [thread["_id"] for thread in threads]},
                "$and": [
                    {"group_id": {"$in": specified_groups_or_global}},
                    {"group_id": {"$exists": False}},
                ],
            }
            group_threads = CommentThread().find(group_query)
            group_thread_ids = [str(thread["_id"]) for thread in group_threads]
            threads_count = len(group_thread_ids)
            comment_thread_ids = filter_standalone_threads(list(comments))

            group_query = {
                "_id": {"$in": [ObjectId(tid) for tid in comment_thread_ids]},
                "$and": [
                    {"group_id": {"$in": specified_groups_or_global}},
                    {"group_id": {"$exists": False}},
                ],
            }
            group_comment_threads = thread_model.find(group_query)
            group_comment_thread_ids = [
                str(thread["_id"]) for thread in group_comment_threads
            ]
            comments_count = sum(
                1
                for comment_thread_id in comment_thread_ids
                if comment_thread_id in group_comment_thread_ids
            )
        else:
            thread_ids = [str(thread["_id"]) for thread in threads]
            threads_count = len(thread_ids)
            comment_thread_ids = filter_standalone_threads(list(comments))
            comments_count = len(comment_thread_ids)

        hash_data.update(
            {
                "threads_count": threads_count,
                "comments_count": comments_count,
            }
        )

    return hash_data


def replace_username_in_all_content(user_id: str, username: str) -> None:
    """Replace new username in all content documents."""
    content_model = Contents()
    contents = content_model.get_list(author_id=user_id)
    for content in contents:
        content_model.update(
            content["_id"],
            author_username=username,
        )


def unsubscribe_all(user_id: str) -> None:
    """Unsubscribe user from all content."""
    subscriptions = Subscriptions()
    subscription_filter = {"subscriber_id": user_id}
    subscriptions_cursor = subscriptions.find(subscription_filter)

    for subscription in subscriptions_cursor:
        subscriptions.delete(subscription["_id"])


def retire_all_content(user_id: str, username: str) -> None:
    """Retire all content from user."""
    content_model = Contents()
    contents = content_model.get_list(author_id=user_id)
    for content in contents:
        content_model.update(
            content["_id"],
            author_username=username,
            body=RETIRED_BODY,
        )
        if content["_type"] == "CommentThread":
            content_model.update(
                content["_id"],
                title=RETIRED_TITLE,
            )


def find_or_create_read_state(user_id: str, thread_id: str) -> dict[str, Any]:
    """Find or create user read states."""
    user = Users().get(user_id)
    if not user:
        raise ObjectDoesNotExist
    thread = CommentThread().get(thread_id)
    if not thread:
        raise ObjectDoesNotExist

    read_states = user.get("read_states", [])
    for state in read_states:
        if state["course_id"] == thread["course_id"]:
            return state

    read_state = {
        "_id": ObjectId(),
        "course_id": thread["course_id"],
        "last_read_times": {},
    }
    read_states.append(read_state)
    Users().update(user_id, read_states=read_states)
    return read_state


def mark_as_read(user: dict[str, Any], thread: dict[str, Any]) -> None:
    """Mark thread as read."""
    read_state = find_or_create_read_state(user["external_id"], thread["_id"])

    read_state["last_read_times"].update(
        {
            str(thread["_id"]): datetime.now(timezone.utc),
        }
    )
    update_user = Users().get(user["external_id"])
    if not update_user:
        raise ObjectDoesNotExist
    new_read_states = update_user["read_states"]
    updated_read_states = []
    for state in new_read_states:
        if state["course_id"] == thread["course_id"]:
            state = read_state
        updated_read_states.append(state)

    Users().update(user["external_id"], read_states=updated_read_states)


def find_or_create_user_stats(user_id: str, course_id: str) -> dict[str, Any]:
    """Find or create user stats document."""
    user = Users().get(user_id)
    if not user:
        raise ObjectDoesNotExist

    course_stats = user.get("course_stats", [])
    for stat in course_stats:
        if stat["course_id"] == course_id:
            return stat

    course_stat = {
        "_id": ObjectId(),
        "active_flags": 0,
        "inactive_flags": 0,
        "threads": 0,
        "responses": 0,
        "replies": 0,
        "course_id": course_id,
        "last_activity_at": "",
    }
    course_stats.append(course_stat)
    Users().update(user["external_id"], course_stats=course_stats)
    return course_stat


def update_user_stats_for_course(user_id: str, stat: dict[str, Any]) -> None:
    """Update user stats for course."""
    user = Users().get(user_id)
    if not user:
        raise ObjectDoesNotExist
    updated_course_stats = []
    course_stats = user["course_stats"]
    for course_stat in course_stats:
        if course_stat["course_id"] == stat["course_id"]:
            course_stat.update(stat)
        updated_course_stats.append(course_stat)
    Users().update(user_id, course_stats=updated_course_stats)


def build_course_stats(author_id: str, course_id: str) -> None:
    """Build course stats."""
    user = Users().get(author_id)
    if not user:
        raise ObjectDoesNotExist
    pipeline = [
        {
            "$match": {
                "course_id": course_id,
                "author_id": user["external_id"],
                "anonymous_to_peers": False,
                "anonymous": False,
            }
        },
        {
            "$addFields": {
                "is_reply": {"$ne": [{"$ifNull": ["$parent_id", None]}, None]}
            }
        },
        {
            "$group": {
                "_id": {"type": "$_type", "is_reply": "$is_reply"},
                "count": {"$sum": 1},
                "active_flags": {
                    "$sum": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$abuse_flaggers"}, 0]},
                            "then": 1,
                            "else": 0,
                        }
                    }
                },
                "inactive_flags": {
                    "$sum": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$historical_abuse_flaggers"}, 0]},
                            "then": 1,
                            "else": 0,
                        }
                    }
                },
                "latest_update_at": {"$max": "$updated_at"},
            }
        },
    ]

    data = list(Contents().aggregate(pipeline))
    active_flags = 0
    inactive_flags = 0
    threads = 0
    responses = 0
    replies = 0
    updated_at = datetime.utcfromtimestamp(0)

    for counts in data:
        _type, is_reply = counts["_id"]["type"], counts["_id"]["is_reply"]
        last_update_at = counts.get("latest_update_at", datetime(1970, 1, 1))
        if _type == "Comment" and is_reply:
            replies = counts["count"]
        elif _type == "Comment" and not is_reply:
            responses = counts["count"]
        else:
            threads = counts["count"]
        last_update_at = make_aware(last_update_at)
        updated_at = make_aware(updated_at)
        updated_at = max(last_update_at, updated_at)
        active_flags += counts["active_flags"]
        inactive_flags += counts["inactive_flags"]

    stats = find_or_create_user_stats(user["external_id"], course_id)
    stats["replies"] = replies
    stats["responses"] = responses
    stats["threads"] = threads
    stats["active_flags"] = active_flags
    stats["inactive_flags"] = inactive_flags
    stats["last_activity_at"] = updated_at
    update_user_stats_for_course(user["external_id"], stats)


def update_all_users_in_course(course_id: str) -> list[str]:
    """Update all user stats in a course."""
    course_contents = Contents().get_list(
        anonymous=False,
        anonymous_to_peers=False,
        course_id=course_id,
    )
    author_ids = []
    for content in course_contents:
        if content["author_id"] not in author_ids:
            author_ids.append(content["author_id"])

    for author_id in author_ids:
        build_course_stats(author_id, course_id)
    return author_ids


def get_user_by_username(username: str | None) -> dict[str, Any] | None:
    """Return user from username."""
    cursor = Users().find({"username": username})
    try:
        return next(cursor)
    except StopIteration:
        return None


def find_or_create_user(user_id: str) -> str:
    """Find or create user."""
    user = Users().get(user_id)
    if user:
        return user["external_id"]
    user_id = Users().insert(user_id)
    return user_id
