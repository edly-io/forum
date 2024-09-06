"""
Elastic Search Index Manager.
"""

from typing import Any, Optional

from django.conf import settings
from elasticsearch import Elasticsearch

from forum.constants import (
    FORUM_ELASTICSEARCH_INDEX_NAMES,
    FORUM_MAX_DEEP_SEARCH_COMMENT_COUNT,
)
from forum.models.threads import CommentThread


class ElasticsearchManager:
    """
    Manager for handling Elastic Search Queries.
    """

    def __init__(self) -> None:
        """
        Init function.
        """
        self.index_names: list[str] = FORUM_ELASTICSEARCH_INDEX_NAMES
        self.max_search_count: int = FORUM_MAX_DEEP_SEARCH_COMMENT_COUNT
        self.client: Elasticsearch = Elasticsearch(settings.ELASTIC_SEARCH_CONFIG)

    def execute_search(
        self,
        must_clause: Optional[list[dict[str, Any]]] = None,
        filter_clause: Optional[list[dict[str, Any]]] = None,
        sort_criteria: Optional[list[dict[str, str]]] = None,
        size: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Execute a search query using Elasticsearch.

        :param must_clause: The 'must' clause for the query
        :param filter_clause: The 'filter' clause for the query
        :param sort_criteria: List of sorting criteria (e.g., [{'updated_at': 'desc'}, {'created_at': 'asc'}])
        :param size: The maximum number of search results to retrieve
        :return: Elasticsearch response
        """
        body: dict[str, Any] = {
            "size": size or self.max_search_count,
            "sort": sort_criteria or [{"updated_at": "desc"}],
            "query": {
                "bool": {"must": must_clause or [], "should": filter_clause or []}
            },
        }
        return self.client.search(index=self.index_names, body=body)

    def get_suggested_text(
        self, search_text: str, suggestion_fields: Optional[list[str]] = None
    ) -> Optional[str]:
        """
        Retrieve text suggestions for a given search query.

        :param search_text: Text to search for suggestions
        :param suggestion_fields: Fields for which to retrieve suggestions (e.g., ["body", "title"])
        :return: Suggested text or None
        """
        if not suggestion_fields:
            suggestion_fields = ["body", "title"]

        suggest_body: dict[str, Any] = {
            "suggest": {
                f"{field}_suggestions": {
                    "text": search_text,
                    "phrase": {"field": field},
                }
                for field in suggestion_fields
            }
        }
        response: dict[str, Any] = self.client.search(
            index=self.index_names, body=suggest_body
        )
        return self._extract_suggestion(
            response, [f"{field}_suggestions" for field in suggestion_fields]
        )

    @staticmethod
    def _extract_suggestion(
        response: dict[str, Any], suggestion_types: list[str]
    ) -> Optional[str]:
        """
        Extract suggestions from the Elasticsearch response.
        """
        for suggestion_type in suggestion_types:
            suggestions: list[dict[str, Any]] = response.get("suggest", {}).get(
                suggestion_type, []
            )
            options = suggestions and suggestions[0].get("options", [])
            if options:
                return options[0]["text"]
        return None


class ThreadSearchManager(ElasticsearchManager):
    """
    Manager for handling Thread Queries.
    """

    def build_must_clause(
        self, params: dict[str, str], search_text: str
    ) -> list[dict[str, Any]]:
        """
        Build the 'must' clause for thread-specific Elasticsearch queries based on input parameters.
        """
        must: list[dict[str, Any]] = []

        if params.get("commentable_id"):
            must.append({"term": {"commentable_id": params["commentable_id"]}})
        if params.get("commentable_ids"):
            must.append(
                {"terms": {"commentable_id": params["commentable_ids"].split(",")}}
            )
        if params.get("course_id"):
            must.append({"term": {"course_id": params["course_id"]}})

        must.append(
            {
                "multi_match": {
                    "query": search_text,
                    "fields": ["title", "body"],
                    "operator": "AND",
                }
            }
        )

        return must

    def build_filter_clause(
        self,
        context: str,
        group_ids: Optional[list[int]] = None,
    ) -> list[dict[str, Any]]:
        """
        Build the 'filter' clause for thread-specific Elasticsearch queries based on context and group parameters.
        """
        filter_clause: list[dict[str, Any]] = []

        filter_clause.extend(
            [
                {"bool": {"must_not": {"exists": {"field": "context"}}}},
                {"term": {"context": context}},
            ]
        )

        if group_ids and len(group_ids) > 1:
            filter_clause.extend(
                [
                    {"bool": {"must_not": {"exists": {"field": "group_id"}}}},
                    {"terms": {"group_id": group_ids}},
                ]
            )

        elif group_ids and len(group_ids) == 1:
            filter_clause.extend(
                [
                    {"bool": {"must_not": {"exists": {"field": "group_id"}}}},
                    {"term": {"group_id": group_ids[0]}},
                ]
            )

        return filter_clause

    def get_thread_ids(
        self,
        context: str,
        group_ids: list[int],
        params: dict[str, str],
        search_text: str,
        sort_criteria: Optional[list[dict[str, str]]] = None,
    ) -> list[str]:
        """
        Retrieve thread IDs based on search criteria.
        """
        must_clause: list[dict[str, Any]] = self.build_must_clause(params, search_text)
        filter_clause: list[dict[str, Any]] = self.build_filter_clause(
            context, group_ids
        )

        response: dict[str, Any] = self.execute_search(
            must_clause, filter_clause, sort_criteria
        )

        if response:
            return list(
                {
                    (
                        hit["_id"]
                        if CommentThread.index_name in hit.get("_index")
                        else hit.get("_source", {}).get("comment_thread_id")
                    )
                    for hit in response.get("hits", {}).get("hits")
                }
            )

        return []

    def get_thread_ids_with_corrected_text(
        self,
        context: str,
        group_ids: list[int],
        params: dict[str, str],
        search_text: str,
        sort_criteria: Optional[list[dict[str, str]]] = None,
    ) -> list[str]:
        """
        The function is just used of mimicing the behaviour of the test cases.
        It's same as of the get_thread_ids but it could be used in the test cases for
        updating the returned values.
        """
        return self.get_thread_ids(
            context, group_ids, params, search_text, sort_criteria
        )
