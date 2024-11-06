"""
Search backend API.
"""

import importlib

from django.conf import settings

from forum.search import base


def get_index_search_backend() -> base.BaseIndexSearchBackend:
    """
    Return backend instance for managing search indices.
    """
    return _get_search_backend().INDEX_SEARCH_CLASS()


def get_document_search_backend() -> base.BaseDocumentSearchBackend:
    """
    Return backend instance for indexing, deleting and updating documents.
    """
    return _get_search_backend().DOCUMENT_SEARCH_CLASS()


def get_thread_search_backend() -> base.BaseThreadSearchBackend:
    """
    Return backend instance for searching thread documents.
    """
    return _get_search_backend().THREAD_SEARCH_CLASS()


def _get_search_backend() -> base.BaseSearchBackend:
    """
    Future-proof backend provider that is compatible with multiple
    backends.

    By default, use the Elasticsearch search backend.
    """
    search_backend_module_name = getattr(
        settings, "FORUM_SEARCH_BACKEND", "forum.search.es.ElasticsearchBackend"
    )
    module_name, class_name = search_backend_module_name.rsplit(".", 1)
    Backend = getattr(importlib.import_module(module_name), class_name)
    return Backend
