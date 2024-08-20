"""
Search API Views
"""

from typing import Any, Dict, List, Optional, Tuple

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.index_manager import ThreadSearchManager
from forum.models.model_utils import handle_threads_query
from forum.serializers.thread import ThreadSerializer


class SearchThreadsView(APIView):
    """
    A view that handles the search and retrieval of threads based on query parameters.

    This view provides a `GET` endpoint that allows searching for threads with various filtering,
    sorting, and pagination options. It also supports suggesting corrected search text if no results
    are found with the initial query.

    Methods:
        get(request): Handles GET requests for searching threads.
        get_group_ids_from_params(params): Extracts group IDs from the query parameters.
    """

    def _validate_request(self, request: Request) -> None:
        """
        Validate query params in the request.
        """
        text = request.GET.get("text")
        sort_key = request.GET.get("sort_key")
        if not text:
            raise ValueError("text is required")
        if sort_key and sort_key not in ["activity", "comments", "date", "votes"]:
            raise ValueError("invalid sort_key")

    def _get_thread_ids_from_indexes(
        self, context: str, group_ids: List[int], params: Dict[str, Any], text: str
    ) -> Tuple[List[str], Optional[str]]:
        """
        Retrieve thread IDs based on the search text and suggested corrections if necessary.

        Args:
            context (str): The context in which the search is performed, e.g., "course".
            group_ids (List[int]): List of group IDs to filter the search.
            params (Dict[str, Any]): Query parameters for the search.
            text (str): The search text used to find threads.

        Returns:
            Tuple[Optional[List[str]], Optional[str]]:
                - A list of thread IDs that match the search criteria.
                - A suggested correction for the search text, or None if no correction is found.
        """
        corrected_text: Optional[str] = None
        search_manager = ThreadSearchManager()

        thread_ids = search_manager.get_thread_ids(context, group_ids, params, text)

        if not thread_ids:
            corrected_text = search_manager.get_suggested_text(text, ["body", "title"])
            if corrected_text:
                thread_ids = search_manager.get_thread_ids(
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
            self._validate_request(request=request)
        except ValueError as error:
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        text: str = request.GET.get("text", "")
        context: str = request.GET.get("context", "course")
        user_id: str = request.GET.get("user_id", "")
        course_id: str = request.GET.get("course_id", "")
        author_id: Optional[str] = request.GET.get("author_id", None)
        thread_type: Optional[str] = request.GET.get("thread_type", None)
        flagged: bool = request.GET.get("flagged") == "true"
        unread: bool = request.GET.get("unread") == "true"
        unanswered: bool = request.GET.get("unanswered") == "true"
        unresponded: bool = request.GET.get("unresponded") == "true"
        count_flagged: bool = request.GET.get("count_flagged") == "true"
        sort_key: Optional[str] = request.GET.get("sort_key")
        page: int = int(request.GET.get("page", "1"))
        per_page: int = int(request.GET.get("per_page", "10"))

        if sort_key not in ["activity", "comments", "date", "votes"]:
            sort_key = "date"

        group_ids: List[int] = self.get_group_ids_from_params(request.GET)

        thread_ids, corrected_text = self._get_thread_ids_from_indexes(
            context, group_ids, request.GET, text
        )

        data: Dict[str, Any] = handle_threads_query(
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

        return Response(data)

    def get_group_ids_from_params(self, params: Dict[str, Any]) -> List[int]:
        """
        Extract group IDs from the query parameters.

        Args:
            params (Dict[str, Any]): Query parameters from the request.

        Returns:
            List[int]: A list of group IDs extracted from the query parameters.
        """
        group_id: Optional[str] = params.get("group_id")
        group_ids: Optional[str] = params.get("group_ids")
        if group_id:
            return [int(group_id)]
        elif group_ids:
            return [int(gid) for gid in group_ids.split(",")]
        return []
