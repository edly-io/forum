#!/usr/bin/env python
"""
Tests for the `Notifications` model.
"""
from bson import ObjectId


def test_insert(notifications_model):
    """Test insert a notification into MongoDB."""
    notification_id = notifications_model.insert(
        notification_type="test_type",
        info={"key": "value"},
        actor_id="actor1",
        target_id="target1",
        receiver_ids=["receiver1", "receiver2"],
    )
    assert notification_id is not None
    notification_data = notifications_model.get(_id=ObjectId(notification_id))
    assert notification_data is not None
    assert notification_data["notification_type"] == "test_type"
    assert notification_data["info"] == {"key": "value"}
    assert notification_data["actor_id"] == "actor1"
    assert notification_data["target_id"] == "target1"
    assert notification_data["receiver_ids"] == ["receiver1", "receiver2"]


def test_delete(notifications_model):
    """Test delete a notification from MongoDB."""
    notification_id = notifications_model.insert(
        notification_type="test_type",
        info={"key": "value"},
        actor_id="actor1",
        target_id="target1",
        receiver_ids=["receiver1", "receiver2"],
    )
    result = notifications_model.delete(ObjectId(notification_id))
    assert result == 1
    notification_data = notifications_model.get(_id=ObjectId(notification_id))
    assert notification_data is None


def test_list(notifications_model):
    """Test list all notifications from MongoDB."""
    notifications_model.collection.insert_many(
        [
            {
                "notification_type": "type1",
                "info": {"key1": "value1"},
                "actor_id": "actor1",
                "target_id": "target1",
                "receiver_ids": ["receiver1"],
            },
            {
                "notification_type": "type2",
                "info": {"key2": "value2"},
                "actor_id": "actor2",
                "target_id": "target2",
                "receiver_ids": ["receiver2"],
            },
            {
                "notification_type": "type3",
                "info": {"key3": "value3"},
                "actor_id": "actor3",
                "target_id": "target3",
                "receiver_ids": ["receiver3"],
            },
        ]
    )
    notifications_list = notifications_model.list()
    assert len(list(notifications_list)) == 3
    assert all(
        notification["notification_type"].startswith("type")
        for notification in notifications_list
    )


def test_update(notifications_model):
    """Test update a notification in MongoDB."""
    notification_id = notifications_model.insert(
        notification_type="test_type",
        info={"key": "value"},
        actor_id="actor1",
        target_id="target1",
        receiver_ids=["receiver1", "receiver2"],
    )

    result = notifications_model.update(
        _id=ObjectId(notification_id),
        notification_type="updated_type",
        info={"key": "new_value"},
        actor_id="new_actor",
        target_id="new_target",
        receiver_ids=["new_receiver"],
    )
    assert result == 1
    notification_data = notifications_model.get(_id=ObjectId(notification_id))
    assert notification_data["notification_type"] == "updated_type"
    assert notification_data["info"] == {"key": "new_value"}
    assert notification_data["actor_id"] == "new_actor"
    assert notification_data["target_id"] == "new_target"
    assert notification_data["receiver_ids"] == ["new_receiver"]
