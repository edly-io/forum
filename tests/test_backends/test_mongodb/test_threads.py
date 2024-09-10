#!/usr/bin/env python
"""
Tests for the `CommentThread` model.
"""

import pytest

from forum.backends.mongodb import CommentThread


def test_insert_invalid_data() -> None:
    """The inserting invalid data"""
    with pytest.raises(ValueError, match="Invalid thread_type"):
        CommentThread().insert(
            title="Test title",
            body="Test body",
            course_id="course_123",
            commentable_id="commentable_123",
            author_id="author_123",
            thread_type="invalid_type",
        )

    with pytest.raises(ValueError, match="Invalid context"):
        CommentThread().insert(
            title="Test title",
            body="Test body",
            course_id="course_123",
            commentable_id="commentable_123",
            author_id="author_123",
            context="invalid_context",
        )


def test_insert() -> None:
    """Test insert a comment thread into MongoDB."""
    thread_id = CommentThread().insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )
    assert thread_id is not None
    thread_data = CommentThread().get(thread_id)
    assert thread_data is not None
    assert thread_data["title"] == "Test Thread"
    assert thread_data["body"] == "This is a test thread"


def test_delete() -> None:
    """Test delete a comment thread from MongoDB."""
    thread_id = CommentThread().insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )
    result = CommentThread().delete(thread_id)
    assert result == 1
    thread_data = CommentThread().get(thread_id)
    assert thread_data is None


def test_list() -> None:
    """Test list all comment threads from MongoDB."""
    CommentThread().insert(
        "Thread 1",
        "Body 1",
        "_type",
        "CommentThread",
        "1",
        "user1",
    )
    CommentThread().insert(
        "Thread 2",
        "Body 2",
        "_type",
        "CommentThread",
        "1",
        "user1",
    )
    CommentThread().insert(
        "Thread 3",
        "Body 3",
        "_type",
        "CommentThread",
        "1",
        "user1",
    )
    threads_list = CommentThread().get_list()
    assert len(list(threads_list)) == 3
    assert all(thread["title"].startswith("Thread") for thread in threads_list)


def test_update() -> None:
    """Test update a comment thread in MongoDB."""
    thread_id = CommentThread().insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )

    result = CommentThread().update(
        thread_id=thread_id,
        title="Updated Title",
        body="Updated body",
        commentable_id="new_commentable_id",
    )
    assert result == 1
    thread_data = CommentThread().get(thread_id)
    assert thread_data is not None
    assert thread_data["title"] == "Updated Title"
    assert thread_data["body"] == "Updated body"
    assert thread_data["commentable_id"] == "new_commentable_id"
