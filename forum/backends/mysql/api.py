"""Client backend for forum v2."""

import math
from datetime import datetime
from typing import Any, Optional, Union

from django.contrib.auth.models import User  # pylint: disable=E5142
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Max, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from forum.backends.mysql.models import (
    AbuseFlagger,
    Comment,
    CommentThread,
    CourseStat,
    ForumUser,
    HistoricalAbuseFlagger,
    LastReadTime,
    ReadState,
    Subscription,
    UserVote,
)
from forum.constants import RETIRED_BODY, RETIRED_TITLE
from forum.utils import get_group_ids_from_params, get_sort_criteria


def update_stats_for_course(user_id: str, course_id: str, **kwargs: Any) -> None:
    """Update stats for a course."""
    user = User.objects.get(pk=user_id)
    course_stat, created = CourseStat.objects.get_or_create(
        user=user, course_id=course_id
    )
    if created:
        course_stat.active_flags = 0
        course_stat.inactive_flags = 0
        course_stat.threads = 0
        course_stat.responses = 0
        course_stat.replies = 0

    for key, value in kwargs.items():
        if hasattr(course_stat, key):
            setattr(course_stat, key, F(key) + value)

    course_stat.save()


def _get_entity_from_type(
    entity_id: str, entity_type: str
) -> Union[Comment, CommentThread]:
    """Get entity from type."""
    if entity_type == "Comment":
        return Comment.objects.get(pk=entity_id)
    else:
        return CommentThread.objects.get(pk=entity_id)


def flag_as_abuse(user_id: str, entity_id: str, entity_type: str) -> dict[str, Any]:
    """Flag an entity as abuse."""
    user = User.objects.get(pk=user_id)
    entity = _get_entity_from_type(entity_id, entity_type)
    abuse_flaggers = entity.abuse_flaggers
    first_flag_added = False
    if user.pk not in abuse_flaggers:
        AbuseFlagger.objects.create(
            user=user, content=entity, flagged_at=timezone.now()
        )
        first_flag_added = len(abuse_flaggers) == 1
    if first_flag_added:
        update_stats_for_course(user_id, entity.course_id, active_flags=1)
    return entity.to_dict()


def un_flag_as_abuse(user_id: str, entity_id: str, entity_type: str) -> dict[str, Any]:
    """Unflag an entity as abuse."""
    user = User.objects.get(pk=user_id)
    entity = _get_entity_from_type(entity_id, entity_type)
    has_no_historical_flags = len(entity.historical_abuse_flaggers) == 0
    if user.pk in entity.abuse_flaggers:
        AbuseFlagger.objects.filter(
            user=user,
            content_object_id=entity.pk,
            content_type=entity.content_type,
        ).delete()
        update_stats_after_unflag(
            entity.author.pk, entity.pk, entity.type, has_no_historical_flags
        )

    return entity.to_dict()


def un_flag_all_as_abuse(entity_id: str, entity_type: str) -> dict[str, Any]:
    """Unflag all users from an entity."""
    entity = _get_entity_from_type(entity_id, entity_type)
    has_no_historical_flags = len(entity.historical_abuse_flaggers) == 0
    historical_abuse_flaggers = list(
        set(entity.historical_abuse_flaggers) | set(entity.abuse_flaggers)
    )
    for flagger_id in historical_abuse_flaggers:
        HistoricalAbuseFlagger.objects.create(
            content=entity,
            user=User.objects.get(pk=flagger_id),
            flagged_at=timezone.now(),
        )
    AbuseFlagger.objects.filter(
        content_object_id=entity.pk, content_type=entity.content_type
    ).delete()
    update_stats_after_unflag(
        entity.author.pk, entity.pk, entity.type, has_no_historical_flags
    )

    return entity.to_dict()


def update_stats_after_unflag(
    user_id: str, entity_id: str, entity_type: str, has_no_historical_flags: bool
) -> None:
    """Update the stats for the course after unflagging an entity."""
    entity = _get_entity_from_type(entity_id, entity_type)
    if not entity:
        raise ObjectDoesNotExist

    first_historical_flag = (
        has_no_historical_flags and not entity.historical_abuse_flaggers
    )
    if first_historical_flag:
        update_stats_for_course(user_id, entity.course_id, inactive_flags=1)

    if not entity.abuse_flaggers:
        update_stats_for_course(user_id, entity.course_id, active_flags=-1)


def update_vote(
    content_id: str,
    content_type: str,
    user_id: str,
    vote_type: str = "",
    is_deleted: bool = False,
) -> bool:
    """
    Update a vote on a thread (either upvote or downvote).

    :param content: The content containing vote data.
    :param user: The user for the user voting.
    :param vote_type: String indicating the type of vote ('up' or 'down').
    :param is_deleted: Boolean indicating if the user is removing their vote (True) or voting (False).
    :return: True if the vote was successfully updated, False otherwise.
    """
    user = User.objects.get(pk=user_id)
    content = _get_entity_from_type(content_id, content_type)
    votes = content.votes
    user_vote = votes.filter(user__pk=user.pk).first()

    if not is_deleted:
        if vote_type not in ["up", "down"]:
            raise ValueError("Invalid vote_type, use ('up' or 'down')")
        if not user_vote:
            user_vote = UserVote.objects.create(user=user, content=content)
        if vote_type == "up":
            user_vote.vote = 1
        else:
            user_vote.vote = -1
        user_vote.save()
        return True
    else:
        if user_vote:
            user_vote.delete()
            return True

    return False


def upvote_content(entity_id: str, entity_type: str, user_id: str) -> bool:
    """
    Upvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be upvoted.
        user (dict): The user who is performing the upvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(entity_id, entity_type, user_id, vote_type="up")


def downvote_content(entity_id: str, entity_type: str, user_id: str) -> bool:
    """
    Downvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be downvoted.
        user (dict): The user who is performing the downvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(entity_id, entity_type, user_id, vote_type="down")


def remove_vote(entity_id: str, entity_type: str, user_id: str) -> bool:
    """
    Remove the vote (upvote or downvote) from the specified thread or comment for the given user.

    Args:
        thread (dict): The thread or comment data from which the vote should be removed.
        user (dict): The user who is removing their vote.

    Returns:
        bool: True if the vote was successfully removed, False otherwise.
    """
    return update_vote(entity_id, entity_type, user_id, is_deleted=True)


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
    try:
        thread = CommentThread.objects.get(pk=thread_id)
        user = ForumUser.objects.get(user__pk=user_id)
    except ObjectDoesNotExist as exc:
        raise ValueError("User / Thread doesn't exist") from exc

    return user.to_dict(), thread.to_dict()


def pin_unpin_thread(thread_id: str, action: str) -> None:
    """
    Pin or unpin the thread based on action parameter.

    Arguments:
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").
    """
    try:
        comment_thread = CommentThread.objects.get(pk=thread_id)
    except ObjectDoesNotExist as exc:
        raise ValueError("Thread doesn't exist") from exc
    comment_thread.pinned = action == "pin"
    comment_thread.save()


def get_pinned_unpinned_thread_serialized_data(
    user_id: str, thread_id: str, serializer_class: Any
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
    user = ForumUser.objects.get(user__pk=user_id)
    updated_thread = CommentThread.objects.get(pk=thread_id)
    user_data = user.to_dict()
    context = {
        "user_id": user_data["_id"],
        "username": user_data["username"],
        "type": "thread",
        "id": thread_id,
    }
    if updated_thread is not None:
        context = {**context, **updated_thread.to_dict()}
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
    return get_pinned_unpinned_thread_serialized_data(
        user["_id"], thread_id, serializer_class
    )


def get_abuse_flagged_count(thread_ids: list[str]) -> dict[str, int]:
    """
    Retrieves the count of abuse-flagged comments for each thread in the provided list of thread IDs.

    Args:
        thread_ids (list[str]): List of thread IDs to check for abuse flags.

    Returns:
        dict[str, int]: A dictionary mapping thread IDs to their corresponding abuse-flagged comment count.
    """
    flagged_threads = (
        Comment.objects.filter(
            comment_thread__pk__in=thread_ids,
            abuse_flaggers__isnull=False,
        )
        .values("comment_thread_id")
        .annotate(flagged_count=Count("id"))
        .order_by()
    )

    result = {
        str(item["comment_thread_id"]): item["flagged_count"]
        for item in flagged_threads
    }
    return result


def get_read_states(
    thread_ids: list[str], user_id: str, course_id: str
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
    read_states: dict[str, list[Any]] = {}
    user = User.objects.get(pk=user_id)
    threads = CommentThread.objects.filter(pk__in=thread_ids)
    read_state = ReadState.objects.filter(user=user, course_id=course_id).first()
    if not read_state:
        return read_states

    read_dates = read_state.last_read_times

    for thread in threads:
        read_date = read_dates.filter(comment_thread=thread).first()
        if not read_date:
            continue

        last_activity_at = thread.last_activity_at
        is_read = read_date.timestamp >= last_activity_at
        unread_comment_count = Comment.objects.filter(
            comment_thread=thread, created_at__gte=read_date, author__pk__ne=user_id
        ).count()
        read_states[thread.pk] = [is_read, unread_comment_count]

    return read_states


def get_filtered_thread_ids(
    thread_ids: list[str], context: str, group_ids: list[str]
) -> set[str]:
    """
    Filters thread IDs based on context and group ID criteria.

    Args:
        thread_ids (list[str]): List of thread IDs to filter.
        context (str): The context to filter by.
        group_ids (list[str]): List of group IDs for group-based filtering.

    Returns:
        set: A set of filtered thread IDs based on the context and group ID criteria.
    """
    context_threads = CommentThread.objects.filter(pk__in=thread_ids, context=context)
    context_thread_ids = set(thread.pk for thread in context_threads)

    if not group_ids:
        return context_thread_ids

    group_threads = CommentThread.objects.filter(
        Q(group_id__in=group_ids) | Q(group_id__isnull=True),
        id__in=thread_ids,
    )
    group_thread_ids = set(thread.pk for thread in group_threads)

    return context_thread_ids.union(group_thread_ids)


def get_endorsed(thread_ids: list[str]) -> dict[str, bool]:
    """
    Retrieves endorsed status for each thread in the provided list of thread IDs.

    Args:
        thread_ids (list[str]): List of thread IDs to check for endorsement.

    Returns:
        dict[str, bool]: A dictionary mapping thread IDs to their endorsed status (True if endorsed, False otherwise).
    """
    endorsed_comments = Comment.objects.filter(
        comment_thread__pk__in=thread_ids, endorsed=True
    )

    return {str(comment.comment_thread.pk): True for comment in endorsed_comments}


def get_user_read_state_by_course_id(user_id: str, course_id: str) -> dict[str, Any]:
    """
    Retrieves the user's read state for a specific course.

    Args:
        user (dict[str, Any]): The user object containing read states.
        course_id (str): The course ID to filter the user's read state by.

    Returns:
        dict[str, Any]: The user's read state for the specified course, or an empty dictionary if not found.
    """
    user = User.objects.get(pk=user_id)
    try:
        read_state = ReadState.objects.get(user=user, course_id=course_id)
    except ObjectDoesNotExist:
        return {}
    return read_state.to_dict()


# TODO: Make this function modular
# pylint: disable=too-many-nested-blocks,too-many-statements
def handle_threads_query(
    comment_thread_ids: list[str],
    user_id: str,
    course_id: str,
    group_ids: list[int],
    author_id: Optional[int],
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
        comment_thread_ids (list[int]): List of comment thread IDs to filter.
        user (User): The user making the request.
        course_id (str): The course ID associated with the threads.
        group_ids (list[int]): List of group IDs for group-based filtering.
        author_id (int): The ID of the author to filter threads by.
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
    user = User.objects.get(pk=user_id)
    # Base query
    base_query = CommentThread.objects.filter(
        pk__in=comment_thread_ids, context=context
    )

    # Group filtering
    if group_ids:
        base_query = base_query.filter(
            Q(group_id__in=group_ids) | Q(group_id__isnull=True)
        )

    # Author filtering
    if author_id:
        base_query = base_query.filter(author__pk=author_id)
        if author_id != user.pk:
            base_query = base_query.filter(anonymous=False, anonymous_to_peers=False)

    # Thread type filtering
    if thread_type:
        base_query = base_query.filter(thread_type=thread_type)

    # Flagged content filtering
    if filter_flagged:
        flagged_comments = Comment.objects.filter(
            course_id=course_id, abuse_flaggers__isnull=False
        ).values_list("comment_thread_id", flat=True)
        flagged_threads = CommentThread.objects.filter(
            course_id=course_id, abuse_flaggers__isnull=False
        ).values_list("id", flat=True)
        base_query = base_query.filter(
            pk__in=list(
                set(comment_thread_ids) & set(flagged_comments) | set(flagged_threads)
            )
        )

    # Unanswered questions filtering
    if filter_unanswered:
        endorsed_threads = Comment.objects.filter(
            course_id=course_id,
            parent__isnull=True,
            endorsed=True,
        ).values_list("comment_thread_id", flat=True)
        base_query = base_query.filter(thread_type="question", id__nin=endorsed_threads)

    # Unresponded threads filtering
    if filter_unresponded:
        base_query = base_query.filter(comment_count=0)

    sort_criteria = get_sort_criteria(sort_key)

    comment_threads = (
        base_query.order_by(sort_criteria) if sort_criteria else base_query
    )
    thread_count = base_query.count()

    if raw_query:
        return {
            "result": [comment_thread.to_dict() for comment_thread in comment_threads]
        }

    if filter_unread and user:
        read_state = get_user_read_state_by_course_id(user.pk, course_id)
        read_dates = read_state.get("last_read_times", {})

        threads: list[str] = []
        skipped = 0
        to_skip = (page - 1) * per_page
        has_more = False

        for thread in comment_threads.iterator():
            thread_key = thread.pk
            if (
                thread_key not in read_dates
                or read_dates[thread_key] < thread.last_activity_at
            ):
                if skipped >= to_skip:
                    if len(threads) == per_page:
                        has_more = True
                        break
                    threads.append(thread.pk)
                else:
                    skipped += 1
        num_pages = page + 1 if has_more else page
    else:
        threads = [thread.pk for thread in comment_threads]
        page = max(1, page)
        start = per_page * (page - 1)
        end = per_page * page
        paginated_collection = threads[start:end]
        threads = list(paginated_collection)
        num_pages = max(1, math.ceil(thread_count / per_page))

    if len(threads) == 0:
        collection = []
    else:
        collection = threads_presentor(threads, user.pk, course_id, count_flagged)

    return {
        "collection": collection,
        "num_pages": num_pages,
        "page": page,
        "thread_count": thread_count,
    }


def prepare_thread(
    thread_id: str,
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
    thread = CommentThread.objects.get(pk=thread_id)
    return {
        **thread.to_dict(),
        "type": "thread",
        "read": is_read,
        "unread_comments_count": unread_count,
        "endorsed": is_endorsed,
        "abuse_flagged_count": abuse_flagged_count,
    }


def threads_presentor(
    thread_ids: list[str],
    user_id: str,
    course_id: str,
    count_flagged: bool = False,
) -> list[dict[str, Any]]:
    """
    Presents the threads by preparing them for display.

    Args:
        threads (list[CommentThread]): List of threads to present.
        user (User): The user presenting the threads.
        course_id (str): The course ID associated with the threads.
        count_flagged (bool, optional): Whether to include flagged content count. Defaults to False.

    Returns:
        list[dict[str, Any]]: A list of prepared thread data.
    """
    threads = CommentThread.objects.filter(pk__in=thread_ids)
    read_states = get_read_states(thread_ids, user_id, course_id)
    threads_endorsed = get_endorsed(thread_ids)
    threads_flagged = get_abuse_flagged_count(thread_ids) if count_flagged else {}

    presenters = []
    for thread in threads:
        is_read, unread_count = read_states.get(
            thread.pk, (False, thread.comment_count)
        )
        is_endorsed = threads_endorsed.get(thread.pk, False)
        abuse_flagged_count = threads_flagged.get(thread.pk, 0)
        presenters.append(
            prepare_thread(
                thread.pk,
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
    try:
        user = User().objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return None
    return user.username


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
    try:
        instance = model.objects.get(pk=int(obj_id))
    except ObjectDoesNotExist as exc:
        raise ObjectDoesNotExist from exc

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
    subscriptions = Subscription.objects.filter(
        subscriber__pk=user_id,
        source_content_type=ContentType.objects.get_for_model(CommentThread),
    )
    thread_ids = [str(subscription.source_object_id) for subscription in subscriptions]
    if course_id:
        thread_ids = list(
            CommentThread.objects.filter(
                pk__in=thread_ids,
                course_id=course_id,
            ).values_list("pk", flat=True)
        )

    return thread_ids


def subscribe_user(
    user_id: str, source_id: str, source_type: str
) -> dict[str, Any] | None:
    """Subscribe a user to a source."""
    subscription, _ = Subscription.objects.get_or_create(
        subscriber__pk=user_id, source__pk=source_id, source_type=source_type
    )
    return subscription.to_dict()


def unsubscribe_user(user_id: str, source_id: str) -> None:
    """Unsubscribe a user from a source."""
    Subscription.objects.filter(subscriber__pk=user_id, source__pk=source_id).delete()


def delete_comments_of_a_thread(thread_id: str) -> None:
    """Delete comments of a thread."""
    Comment.objects.filter(comment_thread__pk=thread_id, parent=None).delete()


def delete_subscriptions_of_a_thread(thread_id: str) -> None:
    """Delete subscriptions of a thread."""
    Subscription.objects.filter(
        source__pk=thread_id,
        source_type=ContentType.objects.get_for_model(CommentThread),
    ).delete()


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
        try:
            User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
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


def get_user_voted_ids(user_id: str, vote: str) -> list[str]:
    """Get the IDs of the posts voted by a user."""
    if vote not in ["up", "down"]:
        raise ValueError("Invalid vote type")

    vote_value = 1 if vote == "up" else -1
    voted_ids = UserVote.objects.filter(user__pk=user_id, vote=vote_value).values_list(
        "content_object_id", flat=True
    )

    return list(voted_ids)


def filter_standalone_threads(comment_thread_ids: list[str]) -> list[str]:
    """Filter out standalone threads from the list of threads."""
    comment_threads = CommentThread.objects.filter(pk__in=comment_thread_ids)
    filtered_threads = [
        thread for thread in comment_threads if thread.context != "standalone"
    ]
    return [str(thread.pk) for thread in filtered_threads]


def user_to_hash(
    user_id: str, params: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Converts user data to a hash
    """
    user = User.objects.get(pk=user_id)
    forum_user = ForumUser.objects.get(user__pk=user_id)
    if params is None:
        params = {}

    user_data = forum_user.to_dict()
    hash_data = {}
    hash_data["username"] = user_data["username"]
    hash_data["external_id"] = user_data["external_id"]

    if params.get("complete"):
        subscribed_thread_ids = find_subscribed_threads(user_id)
        upvoted_ids = get_user_voted_ids(user_id, "up")
        downvoted_ids = get_user_voted_ids(user_id, "down")
        hash_data.update(
            {
                "subscribed_thread_ids": subscribed_thread_ids,
                "subscribed_commentable_ids": [],
                "subscribed_user_ids": [],
                "follower_ids": [],
                "id": user_id,
                "upvoted_ids": upvoted_ids,
                "downvoted_ids": downvoted_ids,
                "default_sort_key": user_data["default_sort_key"],
            }
        )

    if params.get("course_id"):
        threads = CommentThread.objects.filter(
            author=user,
            course_id=params["course_id"],
            anonymous=False,
            anonymous_to_peers=False,
        )
        comments = Comment.objects.filter(
            author=user,
            course_id=params["course_id"],
            anonymous=False,
            anonymous_to_peers=False,
        )
        comment_ids = list(comments.values_list("pk", flat=True))
        if params.get("group_ids"):
            group_threads = threads.filter(group_id__in=params["group_ids"] + [None])
            group_thread_ids = [str(thread.pk) for thread in group_threads]
            threads_count = len(group_thread_ids)
            comment_thread_ids = filter_standalone_threads(comment_ids)

            group_comment_threads = CommentThread.objects.filter(
                id__in=comment_thread_ids, group_id__in=params["group_ids"] + [None]
            )
            group_comment_thread_ids = [
                str(thread.pk) for thread in group_comment_threads
            ]
            comments_count = sum(
                1
                for comment_thread_id in comment_thread_ids
                if comment_thread_id in group_comment_thread_ids
            )
        else:
            thread_ids = [str(thread.pk) for thread in threads]
            threads_count = len(thread_ids)
            comment_thread_ids = filter_standalone_threads(comment_ids)
            comments_count = len(comment_thread_ids)

        hash_data.update(
            {
                "threads_count": threads_count,
                "comments_count": comments_count,
            }
        )

    return hash_data


def unsubscribe_all(user_id: str) -> None:
    """Unsubscribe user from all content."""
    Subscription.objects.filter(subscriber__pk=user_id).delete()


# Kept method signature same as mongo implementation
def retire_all_content(user_id: str, username: str) -> None:  # pylint: disable=W0613
    """Retire all content from user."""
    comments = Comment.objects.filter(author__pk=user_id)
    for comment in comments:
        comment.body = RETIRED_BODY
        comment.save()

    comment_threads = CommentThread.objects.filter(author__pk=user_id)
    for comment_thread in comment_threads:
        comment_thread.body = RETIRED_BODY
        comment_thread.title = RETIRED_TITLE
        comment_thread.save()


def find_or_create_read_state(user_id: str, thread_id: str) -> dict[str, Any]:
    """Find or create user read states."""
    try:
        user = User.objects.get(pk=user_id)
        thread = CommentThread.objects.get(pk=thread_id)
    except (User.DoesNotExist, CommentThread.DoesNotExist) as exc:
        raise ObjectDoesNotExist from exc

    read_state, _ = ReadState.objects.get_or_create(
        user=user, course_id=thread.course_id
    )
    return read_state.to_dict()


def mark_as_read(user_id: str, thread_id: str) -> None:
    """Mark thread as read."""
    user = User.objects.get(pk=user_id)
    thread = CommentThread.objects.get(pk=thread_id)
    read_state, _ = ReadState.objects.get_or_create(
        user=user, course_id=thread.course_id
    )

    LastReadTime.objects.update_or_create(
        read_state=read_state,
        comment_thread=thread,
        defaults={
            "timestamp": timezone.now(),
        },
    )


def find_or_create_user_stats(user_id: str, course_id: str) -> dict[str, Any]:
    """Find or create user stats document."""
    user = User.objects.get(pk=user_id)
    try:
        course_stat = CourseStat.objects.get(user=user, course_id=course_id)
        return course_stat.to_dict()
    except CourseStat.DoesNotExist:
        course_stat = CourseStat(
            user=user,
            course_id=course_id,
            active_flags=0,
            inactive_flags=0,
            threads=0,
            responses=0,
            replies=0,
            last_activity_at=None,
        )
        course_stat.save()
        return course_stat.to_dict()


def update_user_stats_for_course(user_id: str, stat: dict[str, Any]) -> None:
    """Update user stats for course."""
    user = User.objects.get(pk=user_id)
    try:
        course_stat = CourseStat.objects.get(user=user, course_id=stat["course_id"])
        for key, value in stat.items():
            setattr(course_stat, key, value)
        course_stat.save()
    except CourseStat.DoesNotExist:
        course_stat = CourseStat(user=user, **stat)
        course_stat.save()


def build_course_stats(author_id: str, course_id: str) -> None:
    """Build course stats."""
    author = User.objects.get(pk=author_id)
    threads = CommentThread.objects.filter(
        author=author,
        course_id=course_id,
        anonymous_to_peers=False,
        anonymous=False,
    )
    comments = Comment.objects.filter(
        author=author,
        course_id=course_id,
        anonymous_to_peers=False,
        anonymous=False,
    )

    responses = comments.filter(comment_thread__isnull=False)
    replies = comments.filter(comment_thread__isnull=True)

    active_flags = comments.filter(abuse_flaggers__isnull=False).count()
    inactive_flags = comments.filter(historical_abuse_flaggers__isnull=False).count()

    updated_at = max(
        threads.aggregate(Max("updated_at"))["updated_at__max"] or datetime(1970, 1, 1),
        comments.aggregate(Max("updated_at"))["updated_at__max"]
        or datetime(1970, 1, 1),
    )

    stats, _ = CourseStat.objects.get_or_create(user=author, course_id=course_id)
    stats.threads = threads.count()
    stats.responses = responses.count()
    stats.replies = replies.count()
    stats.active_flags = active_flags
    stats.inactive_flags = inactive_flags
    stats.last_activity_at = updated_at
    stats.save()


def update_all_users_in_course(course_id: str) -> list[str]:
    """Update all user stats in a course."""
    course_comments = Comment.objects.filter(
        anonymous=False,
        anonymous_to_peers=False,
        course_id=course_id,
    )
    course_threads = CommentThread.objects.filter(
        anonymous=False,
        anonymous_to_peers=False,
        course_id=course_id,
    )

    comment_authors = set(course_comments.values_list("author__id", flat=True))
    thread_authors = set(course_threads.values_list("author__id", flat=True))
    author_ids = list(comment_authors | thread_authors)

    for author_id in author_ids:
        build_course_stats(author_id, course_id)
    return author_ids


def get_user_by_username(username: str | None) -> dict[str, Any] | None:
    """Return user from username."""
    try:
        return ForumUser.objects.get(user__username=username).to_dict()
    except User.DoesNotExist:
        return None


def find_or_create_user(user_id: str) -> str:
    """Find or create user."""
    user, _ = ForumUser.objects.get_or_create(user__pk=user_id)
    return user.pk


def get_course_id_by_thread_id(thread_id: str) -> str | None:
    """
    Return course_id for the matching thread.
    """
    thread = CommentThread.objects.filter(id=thread_id).first()
    if thread:
        return thread.course_id
    return None


def get_course_id_by_comment_id(comment_id: str) -> str | None:
    """
    Return course_id for the matching comment.
    """
    comment = Comment.objects.filter(id=comment_id).first()
    if comment:
        return comment.course_id
    return None
