# conftest.py
"""
Init file for tests
"""
from unittest.mock import MagicMock, patch

import mongomock
import pytest

from forum.models.threads import CommentThread
from forum.models.users import Users
from forum.mongo import MongoBackend


@pytest.fixture(name="mock_mongo_backend")
def fixture_mock_mongo_backend():
    """Mock MongoClient for tests."""
    client = mongomock.MongoClient()
    db = client["test_forum_db"]

    collections = {
        "contents": db["contents"],
        "users": db["users"],
    }

    mock_backend = MagicMock(spec=MongoBackend)
    for name, collection in collections.items():
        setattr(mock_backend, name, collection)

    return mock_backend


@pytest.fixture(name="patch_mongo_backend")
def fixture_patch_mongo_backend(mock_mongo_backend):
    """Patch the MongoBackend instance with a mock."""
    with patch("forum.mongo.MongoBackend", return_value=mock_mongo_backend):
        yield mock_mongo_backend


@pytest.fixture(name="users_model")
def fixture_users_model(patch_mongo_backend):
    """Get Users model with patched backend"""
    return Users(client=patch_mongo_backend.users)


@pytest.fixture(name="comment_thread_model")
def fixture_comment_thread_model(patch_mongo_backend):
    """Get CommentThread model with patched backend."""
    return CommentThread(client=patch_mongo_backend.contents)