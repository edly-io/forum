"""
Signals for the forum App.
"""

from django.dispatch import Signal

from forum import handlers

# Those objects are useful and should be preserved for testing purposes.
comment_deleted = Signal()
comment_thread_deleted = Signal()
comment_inserted = Signal()
comment_thread_inserted = Signal()
comment_updated = Signal()
comment_thread_updated = Signal()

# Connect the handlers with the search backend
comment_deleted.connect(handlers.handle_comment_deletion)
comment_thread_deleted.connect(handlers.handle_comment_thread_deletion)
comment_inserted.connect(handlers.handle_comment_insertion)
comment_thread_inserted.connect(handlers.handle_comment_thread_insertion)
comment_updated.connect(handlers.handle_comment_updated)
comment_thread_updated.connect(handlers.handle_comment_thread_updated)
