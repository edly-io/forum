"""
Meilisearch backend for search comment and thread objects.
"""

import typing as t

import meilisearch
import search.meilisearch as m
from bs4 import BeautifulSoup
from django.core.paginator import Paginator

from forum import constants
from forum.backends.mysql import MODEL_INDICES
from forum.search import base

FILTERABLE_FIELDS = [
    "context",
    "course_id",
    "commentable_id",
]
INDEXED_FIELDS = ["body", "title"]
ALL_FIELDS = FILTERABLE_FIELDS + INDEXED_FIELDS


class MeilisearchClientMixin:
    """
    Expose a simple meilisearch client property, which is actually a singleton.
    """

    CLIENT: meilisearch.Client | None = None

    @property
    def meilisearch_client(self) -> meilisearch.Client:
        if self.CLIENT is None:
            self.CLIENT = m.get_meilisearch_client()
        return self.CLIENT

    def get_index(self, index_name: str) -> meilisearch.index.Index:
        """
        Get the Meilisearch index associated to a (non-prefixed) name. This index should
        already exist.
        """
        meilisearch_index_name = m.get_meilisearch_index_name(index_name)
        return self.meilisearch_client.get_index(meilisearch_index_name)


def create_document(document: dict[str, t.Any], doc_id: str) -> dict[str, t.Any]:
    """
    We index small documents in Meilisearch, with just a handful of fields.
    """
    # THE CAKE IS A LIE. Sometimes the doc_id is an integer.
    doc_id = str(doc_id)
    processed = {"id": doc_id, m.PRIMARY_KEY_FIELD_NAME: m.id2pk(doc_id)}
    for field in ALL_FIELDS:
        processed[field] = document[field]
    # We remove html markup, which breaks search in some places. For instance
    # "<p>Word" will not match "Word", which is a shame.
    processed["body"] = BeautifulSoup(processed["body"]).get_text()
    return processed


class MeilisearchDocumentBackend(
    base.BaseDocumentSearchBackend, MeilisearchClientMixin
):
    """
    Simple document management.
    """

    def index_document(
        self, index_name: str, doc_id: str, document: dict[str, t.Any]
    ) -> None:
        """
        Insert a single document in the Meilisearch index.
        """
        meilisearch_index = self.get_index(index_name)
        processed = create_document(document, doc_id)
        meilisearch_index.add_documents([processed])

    def update_document(
        self, index_name: str, doc_id: str, update_data: dict[str, t.Any]
    ) -> None:
        """
        Updating is the same as inserting in meilisearch
        """
        return self.index_document(index_name, doc_id, update_data)

    def delete_document(self, index_name: str, doc_id: str) -> None:
        """
        Delete a single document, identified by its ID.
        """
        meilisearch_index = self.get_index(index_name)
        doc_pk = m.id2pk(doc_id)
        meilisearch_index.delete_document(doc_pk)


class MeilisearchIndexBackend(base.BaseIndexSearchBackend, MeilisearchClientMixin):
    """
    Meilisearch index management.
    """

    def initialize_indices(self, force_new_index: bool = False) -> None:
        filterable_fields = [
            m.PRIMARY_KEY_FIELD_NAME,
            "context",
            "course_id",
            "commentable_id",
        ]
        index_filterables = {
            Model.index_name: filterable_fields for Model in MODEL_INDICES
        }
        if force_new_index:
            for index_name in index_filterables:
                meilisearch_index_name = m.get_meilisearch_index_name(index_name)
                task_info = self.meilisearch_client.delete_index(meilisearch_index_name)
                m.wait_for_task_to_succeed(self.meilisearch_client, task_info)
        m.create_indexes(index_filterables=index_filterables)

    def rebuild_indices(
        self, batch_size: int = 500, extra_catchup_minutes: int = 5
    ) -> None:
        """
        Parse model instances and insert them in Meilisearch. Only MySQL-backed
        instances are supported.

        Note that the `extra_catchup_minutes` argument is ignored.
        """
        self.initialize_indices()
        for Model in MODEL_INDICES:
            meilisearch_index = self.get_index(Model.index_name)
            paginator = Paginator(Model.objects.all(), per_page=batch_size)
            for page_number in paginator.page_range:
                page = paginator.get_page(page_number)
                documents = [
                    create_document(obj.doc_to_hash(), obj.id)
                    for obj in page.object_list
                ]
                if documents:
                    meilisearch_index.add_documents(documents)

    def delete_unused_indices(self) -> int:
        """
        This is a no-op, because this search backend does not handle indices like
        Elasticsearch.
        """
        return 0

    def refresh_indices(self) -> None:
        """
        In Meilisearch, this command consists of waiting for pending tasks.
        """
        for enqueued_task in self.meilisearch_client.get_tasks(
            {"statuses": ["enqueued", "processing"]}
        ).results:
            task = self.meilisearch_client.wait_for_task(
                enqueued_task.uid, timeout_in_ms=5000
            )
            if task.status != "succeeded":
                raise RuntimeError(f"Failed meilisearch task: {task}")

    def validate_indices(self) -> None:
        """
        Initialization is in charge of defining filterable fields, so all validation is
        done there.
        """
        self.initialize_indices(force_new_index=False)


class MeilisearchThreadSearchBackend(
    base.BaseThreadSearchBackend, MeilisearchClientMixin
):
    """
    Thread search backend.

    This class is actually much simpler than it's ES equivalent, because it does not
    support text suggestion, nor some of the search parameters (which have little effect anyway).
    """

    def get_thread_ids(
        self,
        context: str,
        # This argument is unsupported. Anyway, its only role was to boost some results,
        # which did not have much effect because they are shuffled anyway downstream.
        group_ids: list[int],
        search_text: str,
        # This parameter is unsupported, but as far as we know it's not used anywhere.
        sort_criteria: t.Optional[list[dict[str, str]]] = None,
        commentable_ids: t.Optional[list[str]] = None,
        course_id: t.Optional[str] = None,
    ) -> list[str]:
        """
        Retrieve thread IDs based on search criteria.
        """
        # Build search parameters
        constraints: dict[str, t.Any] = {
            "context": context,
        }
        if course_id:
            constraints["course_id"] = course_id
        if commentable_ids:
            constraints["commentable_id"] = commentable_ids
        search_params = m.get_search_params(
            size=constants.FORUM_MAX_DEEP_SEARCH_COMMENT_COUNT,
            field_dictionary=constraints,
        )
        search_params["attributesToSearchOn"] = ["title", "body"]

        # Collect thread IDs
        # Note that it's absolutely useless to try to sort threads by score, because
        # results are shuffled downstream. I don't even know why the "title" field is
        # weighted more in the es.py backend...
        thread_ids: set[str] = set()
        for Model in MODEL_INDICES:
            meilisearch_index = self.get_index(Model.index_name)
            results = meilisearch_index.search(search_text, opt_params=search_params)
            for result in results["hits"]:
                thread_id = result.get("comment_thread_id") or result["id"]
                thread_ids.add(thread_id)

        # Don't make the slightest attempt to sort results
        return list(thread_ids)

    def get_suggested_text(self, search_text: str) -> t.Optional[str]:
        """
        Meilisearch does not support query suggestion
        https://github.com/orgs/meilisearch/discussions/740
        """
        return None


class MeilisearchBackend(base.BaseSearchBackend):
    """
    Meilisearch-powered search backend.
    """

    DOCUMENT_SEARCH_CLASS = MeilisearchDocumentBackend
    INDEX_SEARCH_CLASS = MeilisearchIndexBackend
    THREAD_SEARCH_CLASS = MeilisearchThreadSearchBackend
