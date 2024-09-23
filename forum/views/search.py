"""
Search API Views
"""

from typing import Any, Optional

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.constants import FORUM_DEFAULT_PAGE, FORUM_DEFAULT_PER_PAGE
from forum.backends.mongodb.api import handle_threads_query
from forum.search.comment_search import ThreadSearch
from forum.serializers.thread import ThreadSerializer
from forum.utils import get_group_ids_from_params


class SearchThreadsView(APIView):
    """
    A view that handles the search and retrieval of threads based on query parameters.

    This view provides a `GET` endpoint that allows searching for threads with various filtering,
    sorting, and pagination options. It also supports suggesting corrected search text if no results
    are found with the initial query.
    """

    permission_classes = (AllowAny,)

    def _validate_and_extract_params(self, request: Request) -> dict[str, Any]:
        """
        Validate and extract query parameters from the request.
        """
        data = request.query_params
        params: dict[str, Any] = {}

        # Required parameters
        text = data.get("text")
        if not text:
            raise ValueError("text is required")
        params["text"] = text

        # Sort key validation
        VALID_SORT_KEYS = ("activity", "comments", "date", "votes")
        sort_key = data.get("sort_key", "date")
        if sort_key not in VALID_SORT_KEYS:
            raise ValueError("invalid sort_key")
        params["sort_key"] = sort_key

        # Pagination handling
        page = data.get("page", FORUM_DEFAULT_PAGE)
        try:
            params["page"] = int(page)
        except ValueError as exc:
            raise ValueError("Invalid page value.") from exc

        per_page = data.get("per_page", FORUM_DEFAULT_PER_PAGE)
        try:
            params["per_page"] = int(per_page)
        except ValueError as exc:
            raise ValueError("Invalid per_page value.") from exc

        # Optional parameters with default values and type conversion
        params["context"] = data.get("context", "course")
        params["user_id"] = data.get("user_id", "")
        params["course_id"] = data.get("course_id", "")
        params["author_id"] = data.get("author_id")
        params["thread_type"] = data.get("thread_type")
        params["flagged"] = data.get("flagged", "false").lower() == "true"
        params["unread"] = data.get("unread", "false").lower() == "true"
        params["unanswered"] = data.get("unanswered", "false").lower() == "true"
        params["unresponded"] = data.get("unresponded", "false").lower() == "true"
        params["count_flagged"] = data.get("count_flagged", "false").lower() == "true"

        # Group IDs extraction
        params["group_ids"] = get_group_ids_from_params(data)

        return params

    def _get_thread_ids_from_indexes(
        self, context: str, group_ids: list[int], params: dict[str, Any], text: str
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

        thread_ids = thread_search.get_thread_ids(context, group_ids, params, text)
        if not thread_ids:
            corrected_text = thread_search.get_suggested_text(text, ["body", "title"])
            if corrected_text:
                thread_ids = thread_search.get_thread_ids_with_corrected_text(
                    context, group_ids, params, corrected_text
                )
            if not thread_ids:
                corrected_text = None

        return thread_ids, corrected_text

    def get(self, request: Request) -> Response:
        """
        Handle GET requests to search for threads based on query parameters.

        Args:
            request (Request): The Django request object containing query parameters.

        Returns:
            Response: A JSON response containing the search results, corrected text (if any), and total results.
        """

        try:
            params = self._validate_and_extract_params(request)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

        thread_ids, corrected_text = self._get_thread_ids_from_indexes(
            params["context"], params["group_ids"], request.query_params, params["text"]
        )

        data: dict[str, Any] = handle_threads_query(
            thread_ids,
            params["user_id"],
            params["course_id"],
            params["group_ids"],
            params["author_id"],
            params["thread_type"],
            params["flagged"],
            params["unread"],
            params["unanswered"],
            params["unresponded"],
            params["count_flagged"],
            params["sort_key"],
            params["page"],
            params["per_page"],
            params["context"],
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

        return Response(data)
