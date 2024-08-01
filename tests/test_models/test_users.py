#!/usr/bin/env python
"""
Tests for the `forum` models module.
"""

from unittest.mock import MagicMock, patch

import mongomock
import pytest

from forum.models.users import Users
from forum.mongo import MongoBackend


@pytest.fixture(name="mock_mongo_backend")
def fixture_mock_mongo_backend():
    """Mock MongoClient for tests."""
    client = mongomock.MongoClient()
    db = client["test_forum_db"]
    collection = db["test_collection"]
    mock_backend = MagicMock(spec=MongoBackend)
    mock_backend.collection = collection
    return mock_backend


@pytest.fixture(name="patch_mongo_backend")
def fixture_patch_mongo_backend(mock_mongo_backend):
    """Patch the MongoBackend instance with a mock."""
    with patch("forum.mongo.MongoBackend", return_value=mock_mongo_backend):
        yield mock_mongo_backend


@pytest.fixture(name="users_model")
def fixture_users_model(patch_mongo_backend):
    """Get Users model with patched backend"""
    return Users(client=patch_mongo_backend)


def test_get(users_model):
    """Test get user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    users_model.collection.insert_one({
        "external_id": external_id,
        "username": username,
        "email": email,
    })
    user_data = users_model.get(external_id=external_id)
    assert user_data["external_id"] == external_id
    assert user_data["username"] == username
    assert user_data["email"] == email


def test_insert(users_model):
    """Test insert user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    result = users_model.insert(external_id, username, email)
    assert result is not None
    user_data = users_model.get(external_id=external_id)
    assert user_data["external_id"] == external_id
    assert user_data["username"] == username
    assert user_data["email"] == email


def test_delete(users_model):
    """Test delete user from mongodb"""
    external_id = "test_external_id"
    users_model.collection.insert_one({"external_id": external_id})
    result = users_model.delete(external_id)
    assert result == 1
    user_data = users_model.get(external_id=external_id)
    assert user_data is None


def test_list(users_model):
    """Test list user from mongodb"""
    users_model.collection.insert_many([
        {"external_id": "user1", "username": "user1"},
        {"external_id": "user2", "username": "user2"},
        {"external_id": "user3", "username": "user3"},
    ])
    users_list = users_model.list()
    assert len(list(users_list)) == 3
    assert all(user["username"] in ["user1", "user2", "user3"] for user in users_list)


def test_update(users_model):
    """Test update user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    users_model.collection.insert_one({
        "external_id": external_id,
        "username": username,
        "email": email,
    })

    new_username = "new_username"
    new_email = "new_email"
    result = users_model.update(external_id, new_username, new_email)
    assert result is not None

    user_data = users_model.get(external_id=external_id)
    assert user_data["external_id"] == external_id
    assert user_data["username"] == new_username
    assert user_data["email"] == new_email
