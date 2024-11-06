"""
Base abstract classes for search features.

To implement a new search backend, one must implement all the methods both from
BaseDocumentSearchBackend, BaseIndexSearchBackend and BaseThreadSearchBackend. Then, the
SearchBackend.*_CLASS class attributes must be set to the corresponding child classes.
"""

import typing as t


class BaseDocumentSearchBackend:
    """
    Abstract base class for document management.
    """

    def index_document(
        self, index_name: str, doc_id: str, document: dict[str, t.Any]
    ) -> None:
        raise NotImplementedError

    def update_document(
        self, index_name: str, doc_id: str, update_data: dict[str, t.Any]
    ) -> None:
        raise NotImplementedError

    def delete_document(self, index_name: str, doc_id: str) -> None:
        raise NotImplementedError


class BaseIndexSearchBackend:
    """
    Abstract base search backend class for index management.
    """

    def initialize_indices(self, force_new_index: bool = False) -> None:
        raise NotImplementedError

    def rebuild_indices(
        self, batch_size: int = 500, extra_catchup_minutes: int = 5
    ) -> None:
        raise NotImplementedError

    def validate_indices(self) -> None:
        raise NotImplementedError

    def refresh_indices(self) -> None:
        """
        Make sure that all pending changes are applied to the indices.

        This is mostly used in tests.
        """
        raise NotImplementedError

    def delete_unused_indices(self) -> int:
        raise NotImplementedError


class BaseThreadSearchBackend:
    """
    Base class to perform thread search.
    """

    def get_thread_ids(
        self,
        context: str,
        group_ids: list[int],
        search_text: str,
        sort_criteria: t.Optional[list[dict[str, str]]] = None,
        commentable_ids: t.Optional[list[str]] = None,
        course_id: t.Optional[str] = None,
    ) -> list[str]:
        """
        Retrieve thread IDs based on search criteria.
        """
        raise NotImplementedError

    def get_suggested_text(self, search_text: str) -> t.Optional[str]:
        """
        Retrieve text suggestions for a given search query.

        :param search_text: Text to search for suggestions
        :return: Suggested text or None
        """
        raise NotImplementedError

    def get_thread_ids_with_corrected_text(
        self,
        context: str,
        group_ids: list[int],
        search_text: str,
        sort_criteria: t.Optional[list[dict[str, str]]] = None,
        commentable_ids: t.Optional[list[str]] = None,
        course_id: t.Optional[str] = None,
    ) -> list[str]:
        """
        The function is just used of mimicking the behaviour of the test cases.
        It's same as of the get_thread_ids but it could be used in the test cases for
        updating the returned values.
        """
        return self.get_thread_ids(
            context,
            group_ids,
            search_text,
            sort_criteria,
            commentable_ids,
            course_id,
        )


class BaseSearchBackend:
    """
    Abstract base search backend that exposes all search backend features.
    """

    DOCUMENT_SEARCH_CLASS: t.Type[BaseDocumentSearchBackend]
    INDEX_SEARCH_CLASS: t.Type[BaseIndexSearchBackend]
    THREAD_SEARCH_CLASS: t.Type[BaseThreadSearchBackend]
