"""
API for search.
"""

from typing import Any, Optional

from forum.backends.mongodb.api import handle_threads_query
from forum.constants import FORUM_DEFAULT_PAGE, FORUM_DEFAULT_PER_PAGE
from forum.search.comment_search import ThreadSearch
from forum.serializers.thread import ThreadSerializer


def _get_thread_ids_from_indexes(
    context: str,
    group_ids: list[int],
    text: str,
    commentable_id: Optional[str] = None,
    commentable_ids: Optional[str] = None,
    course_id: Optional[str] = None,
) -> tuple[list[str], Optional[str]]:
    """
    Retrieve thread IDs based on the search text and suggested corrections if necessary.

    Args:
        context (str): The context in which the search is performed, e.g., "course".
        group_ids (list[int]): list of group IDs to filter the search.
        params (dict[str, Any]): Query parameters for the search.
        text (str): The search text used to find threads.

    Returns:
        tuple[Optional[list[str]], Optional[str]]:
            - A list of thread IDs that match the search criteria.
            - A suggested correction for the search text, or None if no correction is found.
    """
    corrected_text: Optional[str] = None
    thread_search = ThreadSearch()

    thread_ids = thread_search.get_thread_ids(
        context,
        group_ids,
        text,
        commentable_id=commentable_id,
        commentable_ids=commentable_ids,
        course_id=course_id,
    )
    if not thread_ids:
        corrected_text = thread_search.get_suggested_text(text, ["body", "title"])
        if corrected_text:
            thread_ids = thread_search.get_thread_ids_with_corrected_text(
                context,
                group_ids,
                corrected_text,
                commentable_id=commentable_id,
                commentable_ids=commentable_ids,
                course_id=course_id,
            )
        if not thread_ids:
            corrected_text = None

    return thread_ids, corrected_text


def search_threads(
    text: str,
    sort_key: str,
    context: str,
    user_id: str,
    course_id: str,
    group_ids: list[int],
    author_id: str,
    thread_type: str,
    flagged: bool,
    unread: bool,
    unanswered: bool,
    unresponded: bool,
    count_flagged: bool,
    commentable_id: str,
    commentable_ids: str,
    page: int = FORUM_DEFAULT_PAGE,
    per_page: int = FORUM_DEFAULT_PER_PAGE,
) -> dict[str, Any]:
    """
    Search for threads based on the provided data.
    """
    thread_ids, corrected_text = _get_thread_ids_from_indexes(
        context, group_ids, text, commentable_id, commentable_ids, course_id
    )

    data = handle_threads_query(
        thread_ids,
        user_id,
        course_id,
        group_ids,
        author_id,
        thread_type,
        flagged,
        unread,
        unanswered,
        unresponded,
        count_flagged,
        sort_key,
        page,
        per_page,
        context,
    )

    if collections := data.get("collection"):
        thread_serializer = ThreadSerializer(
            collections,
            many=True,
            context={
                "count_flagged": True,
                "include_endorsed": True,
                "include_read_state": True,
            },
        )
        data["collection"] = thread_serializer.data

    if data:
        data["corrected_text"] = corrected_text
        data["total_results"] = len(thread_ids)

    return data
