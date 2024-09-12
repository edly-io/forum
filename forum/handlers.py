"""
Handlers for the forum app.
"""

import logging
from typing import Any

from forum.search.backend import get_search_backend
from forum.utils import get_str_value_from_collection

log = logging.getLogger(__name__)


def handle_comment_thread_deletion(sender: Any, **kwargs: dict[str, str]) -> None:
    """
    Handle the deletion of a comment thread from the Elasticsearch index.

    Args:
        sender (Any): The model class that sends the signal.
        **kwargs (dict[str, Any]): Additional arguments, including 'comment_thread_id'.
    """
    thread_id = get_str_value_from_collection(kwargs, "comment_thread_id")
    search_backend = get_search_backend()
    search_backend.delete_document(sender.index_name, thread_id)


def handle_comment_deletion(sender: Any, **kwargs: dict[str, Any]) -> None:
    """
    Handle the deletion of a comment from the Elasticsearch index.

    Args:
        sender (Any): The model class that sends the signal.
        **kwargs (dict[str, Any]): Additional arguments, including 'comment_id'.
    """
    comment_id = get_str_value_from_collection(kwargs, "comment_id")
    search_backend = get_search_backend()
    search_backend.delete_document(sender.index_name, comment_id)


def handle_comment_thread_insertion(sender: Any, **kwargs: dict[str, Any]) -> None:
    """
    Handle the insertion of a comment thread into the Elasticsearch index.

    Args:
        sender (Any): The model class that sends the signal.
        **kwargs (dict[str, Any]): Additional arguments, including 'comment_thread_id'.
    """
    thread_id = get_str_value_from_collection(kwargs, "comment_thread_id")
    if thread_id:
        thread = sender().get(_id=thread_id)
        search_backend = get_search_backend()
        doc = sender().doc_to_hash(thread)
        search_backend.index_document(sender.index_name, thread_id, doc)
        log.info(f"Thread {thread_id} added to Elasticsearch index")


def handle_comment_insertion(sender: Any, **kwargs: dict[str, Any]) -> None:
    """
    Handle the insertion of a comment into the Elasticsearch index.

    Args:
        sender (Any): The model class that sends the signal.
        **kwargs (dict[str, Any]): Additional arguments, including 'comment_id'.
    """
    comment_id = get_str_value_from_collection(kwargs, "comment_id")
    if comment_id:
        comment = sender().get(_id=comment_id)
        search_backend = get_search_backend()
        doc = sender().doc_to_hash(comment)
        search_backend.index_document(sender.index_name, comment_id, doc)
        log.info(f"Comment {comment_id} added to Elasticsearch index")


def handle_comment_thread_updated(sender: Any, **kwargs: dict[str, Any]) -> None:
    """
    Handle the update of a comment thread in the Elasticsearch index.

    Args:
        sender (Any): The model class that sends the signal.
        **kwargs (dict[str, Any]): Additional arguments, including 'comment_thread_id'.
    """
    thread_id = get_str_value_from_collection(kwargs, "comment_thread_id")
    if thread_id:
        thread = sender().get(_id=thread_id)
        search_backend = get_search_backend()
        doc = sender().doc_to_hash(thread)
        search_backend.update_document(sender.index_name, thread_id, doc)
        log.info(f"Thread {thread_id} added to Elasticsearch index")


def handle_comment_updated(sender: Any, **kwargs: dict[str, Any]) -> None:
    """
    Handle the update of a comment in the Elasticsearch index.

    Args:
        sender (Any): The model class that sends the signal.
        **kwargs (dict[str, Any]): Additional arguments, including 'comment_id'.
    """
    comment_id = get_str_value_from_collection(kwargs, "comment_id")
    if comment_id:
        comment = sender().get(_id=comment_id)
        search_backend = get_search_backend()
        doc = sender().doc_to_hash(comment)
        search_backend.update_document(sender.index_name, comment_id, doc)
        log.info(f"Comment {comment_id} added to Elasticsearch index")
