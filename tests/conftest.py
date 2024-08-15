# conftest.py
"""
Init file for tests.
"""

import json
from typing import Any, Generator, Union

import mongomock
import pytest
from django.http.response import HttpResponse
from django.test import Client
from pymongo import MongoClient


@pytest.fixture(autouse=True)
def patch_default_mongo_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock default mongodb database for tests."""
    client: MongoClient[Any] = mongomock.MongoClient()
    monkeypatch.setattr(
        "forum.models.base_model.MongoBaseModel.MONGODB_DATABASE",
        client["test_forum_db"],
    )


class APIClient(Client):
    """
    Extends the Django test client to include a custom PUT method.

    This client sends JSON data with the correct headers.
    """

    def put(  # type: ignore[override,no-untyped-def] # pylint: disable=arguments-differ
        self, path: str, data: Any, **kwargs
    ) -> Union[HttpResponse, Any]:
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
def fixture_api_client() -> Generator[APIClient, Any, Any]:
    """Create an API client for testing."""
    client = APIClient()
    yield client
