"""
Init file for tests.
"""

from typing import Any, Callable, Generator
from unittest.mock import patch

import mongomock
import pytest
from pymongo import MongoClient

from forum.backends.mysql.api import MySQLBackend
from forum.backends.mongodb.api import MongoBackend
from test_utils.client import APIClient
from test_utils.mock_es_backend import MockElasticsearchBackend


@pytest.fixture(autouse=True)
def patch_default_mongo_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock default mongodb database for tests."""
    client: MongoClient[Any] = mongomock.MongoClient()
    monkeypatch.setattr(
        "forum.backends.mongodb.base_model.MongoBaseModel.MONGODB_DATABASE",
        client["test_forum_db"],
    )


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture(autouse=True)
def mock_elasticsearch_backend() -> Generator[Any, Any, Any]:
    """Mock the dummy elastic search."""
    with patch("forum.search.backend.ElasticsearchBackend", MockElasticsearchBackend):
        yield


@pytest.fixture(params=[MongoBackend, MySQLBackend], autouse=True)
def patch_get_backend(request: pytest.FixtureRequest) -> Generator[Any, Any, Any]:
    """Mock the get_backend function for both Mongo and MySQL backends."""
    backend_class = request.param

    def backend_factory() -> Callable[[], MongoBackend | MySQLBackend]:
        return backend_class()

    with patch("forum.backend.get_backend", return_value=backend_factory):
        yield
