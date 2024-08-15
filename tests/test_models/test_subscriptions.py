#!/usr/bin/env python
"""
Tests for the Subscriptions model.
"""

from forum.models import Subscriptions


def test_get() -> None:
    """Test get subscription from mongodb"""
    subscriber_id = "test_subscriber_id"
    source_id = "test_source_id"
    source_type = "test_source_type"
    Subscriptions().insert(
        subscriber_id,
        source_id,
        source_type,
    )
    subscription_data = Subscriptions().get_subscription(subscriber_id, source_id)
    assert subscription_data is not None
    assert subscription_data["subscriber_id"] == subscriber_id
    assert subscription_data["source_id"] == source_id
    assert subscription_data["source_type"] == source_type


def test_insert() -> None:
    """Test insert subscription from mongodb"""
    subscriber_id = "test_subscriber_id"
    source_id = "test_source_id"
    source_type = "test_source_type"
    result = Subscriptions().insert(subscriber_id, source_id, source_type)
    assert result is not None
    subscription_data = Subscriptions().get_subscription(subscriber_id, source_id)
    assert subscription_data is not None
    assert subscription_data["subscriber_id"] == subscriber_id
    assert subscription_data["source_id"] == source_id
    assert subscription_data["source_type"] == source_type


def test_delete() -> None:
    """Test delete subscription from mongodb"""
    subscriber_id = "test_subscriber_id"
    source_id = "test_source_id"
    source_type = "test_source_type"
    Subscriptions().insert(subscriber_id, source_id, source_type)
    result = Subscriptions().delete_subscription(subscriber_id, source_id)
    assert result == 1
    subscription_data = Subscriptions().get_subscription(subscriber_id, source_id)
    assert subscription_data is None


def test_list() -> None:
    """Test list subscription from mongodb"""
    Subscriptions().insert(
        subscriber_id="user1",
        source_id="source1",
        source_type="type1",
    )
    Subscriptions().insert(
        subscriber_id="user2",
        source_id="source2",
        source_type="type2",
    )
    Subscriptions().insert(
        subscriber_id="user3",
        source_id="source3",
        source_type="type3",
    )
    subscriptions_list = Subscriptions().list()
    assert len(list(subscriptions_list)) == 3
    assert all(
        subscription["subscriber_id"] in ["user1", "user2", "user3"]
        for subscription in subscriptions_list
    )


def test_update() -> None:
    """Test update subscription from mongodb"""
    subscriber_id = "test_subscriber_id"
    source_id = "test_source_id"
    source_type = "test_source_type"
    Subscriptions().insert(
        subscriber_id=subscriber_id,
        source_id=source_id,
        source_type=source_type,
    )

    new_source_type = "new_source_type"
    result = Subscriptions().update(
        subscriber_id,
        source_id,
        source_type=new_source_type,
    )
    assert result is not None
    assert result == 1

    subscription_data = Subscriptions().get_subscription(subscriber_id, source_id)
    assert subscription_data is not None
    assert subscription_data["subscriber_id"] == subscriber_id
    assert subscription_data["source_id"] == source_id
    assert subscription_data["source_type"] == new_source_type
