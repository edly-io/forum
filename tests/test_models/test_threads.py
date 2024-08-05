#!/usr/bin/env python
"""
Tests for the `CommentThread` model.
"""
from bson import ObjectId


def test_insert(comment_thread_model):
    """Test insert a comment thread into MongoDB."""
    thread_id = comment_thread_model.insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )
    assert thread_id is not None
    thread_data = comment_thread_model.get(_id=ObjectId(thread_id))
    assert thread_data is not None
    assert thread_data["title"] == "Test Thread"
    assert thread_data["body"] == "This is a test thread"


def test_delete(comment_thread_model):
    """Test delete a comment thread from MongoDB."""
    thread_id = comment_thread_model.insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )
    result = comment_thread_model.delete(ObjectId(thread_id))
    assert result == 1
    thread_data = comment_thread_model.get(_id=ObjectId(thread_id))
    assert thread_data is None


def test_list(comment_thread_model):
    """Test list all comment threads from MongoDB."""
    comment_thread_model.collection.insert_many(
        [
            {"title": "Thread 1", "body": "Body 1", "_type": "CommentThread"},
            {"title": "Thread 2", "body": "Body 2", "_type": "CommentThread"},
            {"title": "Thread 3", "body": "Body 3", "_type": "CommentThread"},
        ]
    )
    threads_list = comment_thread_model.list()
    assert len(list(threads_list)) == 3
    assert all(thread["title"].startswith("Thread") for thread in threads_list)


def test_update(comment_thread_model):
    """Test update a comment thread in MongoDB."""
    thread_id = comment_thread_model.insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )

    result = comment_thread_model.update(
        thread_id=ObjectId(thread_id),
        title="Updated Title",
        body="Updated body",
        commentable_id="new_commentable_id",
    )
    assert result == 1
    thread_data = comment_thread_model.get(_id=ObjectId(thread_id))
    assert thread_data["title"] == "Updated Title"
    assert thread_data["body"] == "Updated body"
    assert thread_data["commentable_id"] == "new_commentable_id"
