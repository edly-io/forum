#!/usr/bin/env python
"""
Tests for the `forum` models module.
"""


def test_get(users_model):
    """Test get user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    users_model.collection.insert_one(
        {
            "_id": external_id,
            "external_id": external_id,
            "username": username,
            "email": email,
        }
    )
    user_data = users_model.get(external_id=external_id)
    assert user_data["_id"] == external_id
    assert user_data["external_id"] == external_id
    assert user_data["username"] == username
    assert user_data["email"] == email


def test_insert(users_model):
    """Test insert user from mongodb"""
    user_data = {
        "_id": "test_external_id",
        "external_id": "test_external_id",
        "username": "test_username",
        "email": "test_email",
    }
    result = users_model.insert(**user_data)
    assert result is not None
    fetched_user = users_model.get(_id=user_data["_id"])
    assert fetched_user["_id"] == user_data["external_id"]
    assert fetched_user["external_id"] == user_data["external_id"]
    assert fetched_user["username"] == user_data["username"]
    assert fetched_user["email"] == user_data["email"]


def test_delete(users_model):
    """Test delete user from mongodb"""
    external_id = "test_external_id"
    users_model.collection.insert_one({"_id": external_id, "external_id": external_id})
    result = users_model.delete(external_id)
    assert result == 1
    user_data = users_model.get(external_id=external_id)
    assert user_data is None


def test_list(users_model):
    """Test list user from mongodb"""
    users_model.collection.insert_many(
        [
            {"_id": "user1", "external_id": "user1", "username": "user1"},
            {"_id": "user2", "external_id": "user2", "username": "user2"},
            {"_id": "user3", "external_id": "user3", "username": "user3"},
        ]
    )
    users_list = users_model.list()
    assert len(list(users_list)) == 3
    assert all(user["username"] in ["user1", "user2", "user3"] for user in users_list)


def test_update(users_model):
    """Test update user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    users_model.collection.insert_one(
        {
            "_id": external_id,
            "external_id": external_id,
            "username": username,
            "email": email,
        }
    )

    new_username = "new_username"
    new_email = "new_email"
    user_new_data = {
        "external_id": external_id,
        "username": new_username,
        "email": new_email,
    }
    result = users_model.update(**user_new_data)
    assert result is not None
    assert result == 1
    user_data = users_model.get(external_id=external_id)
    assert user_data["username"] == new_username
    assert user_data["email"] == new_email
