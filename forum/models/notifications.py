"""
Notification Class for Mongo backend.
"""

from forum.models.base_model import MongoBaseModel


class Notifications(MongoBaseModel):
    """
    Notifications class for cs_comments_service notification model
    """

    # TODO: there's no collection named as notifications in mongo db
    # change the below collection name where notifications are being saved
    def __init__(self, collection_name="notifications", client=None):
        """
        Initializes the Notifications class.

        Args:
            collection_name: The name of the MongoDB collection.
            client: The MongoDB client.
        """
        super().__init__(collection_name, client)

    def insert(self, **kwargs) -> str:
        """
        Inserts a new notification document into the database.

        Args:
            notification_type: The type of notification.
            info: Additional information about the notification.
            actor_id: The ID of the user who triggered the notification.
            target_id: The new ID of the target object(e.g. ID of post, thread or comment
                        on which user has liked or commented) of the notification.
            receiver_ids: List of user IDs who should receive the notification.

        Returns:
            The ID of the inserted document.
        """
        notification_data = {
            "notification_type": kwargs.get("notification_type"),
            "info": kwargs.get("info"),
            "receiver_ids": kwargs.get("receiver_ids", []),
        }
        if "actor_id" in kwargs:
            notification_data["actor_id"] = kwargs["actor_id"]
        if "target_id" in kwargs:
            notification_data["target_id"] = kwargs["target_id"]
        result = self.collection.insert_one(notification_data)
        return str(result.inserted_id)

    def update(self, _id: str, **kwargs) -> int:
        """
        Updates a notification document in the database based on the id.

        Args:
            _id: The ID of the notification.
            notification_type: The new type of notification.
            info: The new additional information about the notification.
            actor_id: The new ID of the user who triggered the notification.
            target_id: The new ID of the target object(e.g. ID of post, thread or comment
                        on which user has liked or commented) of the notification.
            receiver_ids: The new list of user IDs who should receive the notification.

        Returns:
            The number of documents modified.
        """
        update_data = {}
        if "notification_type" in kwargs:
            update_data["notification_type"] = kwargs["notification_type"]
        if "info" in kwargs:
            update_data["info"] = kwargs["info"]
        if "actor_id" in kwargs:
            update_data["actor_id"] = kwargs["actor_id"]
        if "target_id" in kwargs:
            update_data["target_id"] = kwargs["target_id"]
        if "receiver_ids" in kwargs:
            update_data["receiver_ids"] = kwargs["receiver_ids"]

        result = self.collection.update_one(
            {"_id": _id},
            {"$set": update_data},
        )
        return result.modified_count
