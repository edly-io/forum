# conftest.py
"""
Init file for tests.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import mongomock
from django.test import Client

from forum.models.contents import Contents
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
    """Get Users model with patched backend."""
    return Users(client=patch_mongo_backend.users)


@pytest.fixture(name="comment_thread_model")
def fixture_comment_thread_model(patch_mongo_backend):
    """Get CommentThread model with patched backend."""
    return CommentThread(client=patch_mongo_backend.contents)


@pytest.fixture(name="content_model")
def fixture_content_model(patch_mongo_backend):
    """Get Contents model with patched backend."""
    return Contents(client=patch_mongo_backend.contents)


class APIClient(Client):
    """
    Extends the Django test client to include a custom PUT method.

    This client sends JSON data with the correct headers.
    """

    def put(self, path, data, **kwargs):  # pylint: disable=arguments-differ
        """
        Send a PUT request with JSON data.

        Args:
            path (str): The URL path to send the request to.
            data (dict): The data to be sent in the request body.
            **kwargs: Additional keyword arguments to be passed to the parent method.

        Returns:
            The response object from the request.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "HTTP_X_API_KEY": "your_api_key",
        }
        return super().put(path, data=json.dumps(data), headers=headers, **kwargs)


@pytest.fixture(name="api_client")
def fixture_api_client():
    """Create an API client for testing."""
    client = APIClient()
    yield client
