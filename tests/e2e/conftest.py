"""
Init file for tests.
"""

import logging
import time

import pytest
from pymongo.errors import ServerSelectionTimeoutError

from forum.mongo import get_database
from forum.search.es import ElasticsearchIndexBackend
from test_utils.client import APIClient

log = logging.getLogger(__name__)

ES_TIMEOUT = 60
MONGO_TIMEOUT = 60
SLEEP_INTERVAL = 5


@pytest.fixture(name="api_client")
def fixture_api_client() -> APIClient:
    """Create an API client for testing."""
    return APIClient()


def wait_for_mongodb() -> None:
    """Wait for MongoDB to start."""
    db = get_database()
    timeout = ES_TIMEOUT
    while timeout > 0:
        try:
            db.command("ping")
            log.info("Connected to the MongoDB")
            return
        except ServerSelectionTimeoutError:
            log.info("Waiting for mongodb to connect")
            time.sleep(SLEEP_INTERVAL)
            timeout -= SLEEP_INTERVAL
    raise Exception("Elasticsearch did not start in time")


def wait_for_elasticsearch() -> None:
    """Wait for ElasticSearch to start."""
    es = ElasticsearchIndexBackend()
    timeout = ES_TIMEOUT
    while timeout > 0:
        if es.client.ping():
            log.info("Connected to the Elastic Search")
            return
        log.info("Waiting for elasticsearch to connect")
        time.sleep(SLEEP_INTERVAL)
        timeout -= SLEEP_INTERVAL
    raise Exception("Elasticsearch did not start in time")


@pytest.fixture(autouse=True)
def initialize_indices() -> None:
    """Initialize Elasticsearch indices."""
    wait_for_elasticsearch()
    es = ElasticsearchIndexBackend()
    es.client.indices.delete(index="*")
    es.initialize_indices()


@pytest.fixture(autouse=True)
def mongo_cleanup() -> None:
    """Cleanup MongoDB collections after each test."""
    wait_for_mongodb()
    db = get_database()

    # Clean up collections after each test case
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)


@pytest.fixture(autouse=True)
def patch_default_mongo_database() -> None:
    """Override the patch statement."""


@pytest.fixture(autouse=True)
def mock_elasticsearch_backend() -> None:
    """Overide teh mocked backend to use actual backend."""
