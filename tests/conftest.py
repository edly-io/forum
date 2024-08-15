# conftest.py
"""
Init file for tests.
"""

from typing import Any

import mongomock
import pytest
from pymongo import MongoClient

from test_utils.client import APIClient


@pytest.fixture(autouse=True)
def patch_default_mongo_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock default mongodb database for tests."""
    client: MongoClient[Any] = mongomock.MongoClient()
    monkeypatch.setattr(
        "forum.models.base_model.MongoBaseModel.MONGODB_DATABASE",
        client["test_forum_db"],
    )


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Create an API client for testing."""
    return APIClient()
