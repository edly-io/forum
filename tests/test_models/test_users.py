#!/usr/bin/env python
"""
Tests for the `forum` models module.
"""

from forum.models import Users


def test_get(users_model: Users) -> None:
    """Test get user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    users_model.insert(
        external_id,
        username,
        email,
    )
    user_data = users_model.get(external_id)
    assert user_data is not None
    assert user_data["_id"] == external_id
    assert user_data["external_id"] == external_id
    assert user_data["username"] == username
    assert user_data["email"] == email


def test_insert(users_model: Users) -> None:
    """Test insert user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    result = users_model.insert(external_id, username, email)
    assert result is not None
    user_data = users_model.get(external_id)
    assert user_data is not None
    assert user_data["_id"] == external_id
    assert user_data["external_id"] == external_id
    assert user_data["username"] == username
    assert user_data["email"] == email


def test_delete(users_model: Users) -> None:
    """Test delete user from mongodb"""
    external_id = "test_external_id"
    users_model.insert(external_id, "test_username", "test_email")
    result = users_model.delete(external_id)
    assert result == 1
    user_data = users_model.get(external_id)
    assert user_data is None


def test_list(users_model: Users) -> None:
    """Test list user from mongodb"""
    users_model.insert(
        external_id="user1",
        username="user1",
        email="user1",
    )
    users_model.insert(
        external_id="user2",
        username="user2",
        email="user1",
    )
    users_model.insert(
        external_id="user3",
        username="user3",
        email="user1",
    )
    users_list = users_model.list()
    assert len(list(users_list)) == 3
    assert all(user["username"] in ["user1", "user2", "user3"] for user in users_list)


def test_update(users_model: Users) -> None:
    """Test update user from mongodb"""
    external_id = "test_external_id"
    username = "test_username"
    email = "test_email"
    users_model.insert(
        external_id=external_id,
        username=username,
        email=email,
    )

    new_username = "new_username"
    new_email = "new_email"
    result = users_model.update(
        external_id,
        username=new_username,
        email=new_email
    )
    assert result is not None
    assert result == 1

    user_data = users_model.get(external_id)
    assert user_data is not None
    assert user_data["external_id"] == external_id
    assert user_data["username"] == new_username
    assert user_data["email"] == new_email
