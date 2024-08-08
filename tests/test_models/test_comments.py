#!/usr/bin/env python
"""
Tests for the `Comment` model.
"""
from bson import ObjectId


def test_insert(comment_model):
    """Test insert a comment into MongoDB."""
    comment_id = comment_model.insert(
        body="<p>This is a test comment</p>",
        course_id="course1",
        comment_thread_id="66af33634a1e1f001b7ed57f",
        author_id="author1",
        author_username="author_user",
    )
    assert comment_id is not None
    comment_data = comment_model.get(_id=ObjectId(comment_id))
    assert comment_data is not None
    assert comment_data["body"] == "<p>This is a test comment</p>"


def test_delete(comment_model):
    """Test delete a comment from MongoDB."""
    comment_id = comment_model.insert(
        body="<p>This is a test comment</p>",
        course_id="course1",
        comment_thread_id="66af33634a1e1f001b7ed57f",
        author_id="author1",
        author_username="author_user",
    )
    result = comment_model.delete(ObjectId(comment_id))
    assert result == 1
    comment_data = comment_model.get(_id=ObjectId(comment_id))
    assert comment_data is None


def test_list(comment_model):
    """Test list all comments from MongoDB."""
    comment_model.collection.insert_many(
        [
            {"body": "<p>Comment 1</p>", "_type": "Comment"},
            {"body": "<p>Comment 2</p>", "_type": "Comment"},
            {"body": "<p>Comment 3</p>", "_type": "Comment"},
        ]
    )
    comments_list = comment_model.list()
    assert len(list(comments_list)) == 3
    assert all(comment["body"].startswith("<p>Comment") for comment in comments_list)


def test_update(comment_model):
    """Test update a comment in MongoDB."""
    comment_id = comment_model.insert(
        body="<p>This is a test comment</p>",
        course_id="course1",
        comment_thread_id="66af33634a1e1f001b7ed57f",
        author_id="author1",
        author_username="author_user",
    )

    result = comment_model.update(
        comment_id=ObjectId(comment_id),
        body="<p>Updated comment</p>",
    )
    assert result == 1
    comment_data = comment_model.get(_id=ObjectId(comment_id))
    assert comment_data["body"] == "<p>Updated comment</p>"
