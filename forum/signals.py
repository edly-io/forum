"""
Signals for the forum App.
"""

from django.dispatch import Signal
from django.conf import settings

from forum.handlers import (
    handle_comment_deletion,
    handle_comment_insertion,
    handle_comment_thread_deletion,
    handle_comment_thread_insertion,
    handle_comment_thread_updated,
    handle_comment_updated,
)

comment_deleted = Signal()
comment_thread_deleted = Signal()
comment_inserted = Signal()
comment_thread_inserted = Signal()
comment_updated = Signal()
comment_thread_updated = Signal()

if settings.FORUM_ENABLE_ELASTIC_SEARCH:
    # Connect the handlers when FORUM_ENABLE_ELASTIC_SEARCH is enabled.
    comment_deleted.connect(handle_comment_deletion)
    comment_thread_deleted.connect(handle_comment_thread_deletion)
    comment_inserted.connect(handle_comment_insertion)
    comment_thread_inserted.connect(handle_comment_thread_insertion)
    comment_updated.connect(handle_comment_updated)
    comment_thread_updated.connect(handle_comment_thread_updated)
