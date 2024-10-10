"""Subscriptions class for mongo backend."""

from datetime import datetime, timezone
from typing import Any, Optional

from forum.backends.mongodb.base_model import MongoBaseModel


class Subscriptions(MongoBaseModel):
    """
    Represents a subscription to a source in the MongoDB database.

    This class provides methods for inserting, updating, retrieving, and listing subscriptions.
    """

    COLLECTION_NAME: str = "subscriptions"

    def insert(self, subscriber_id: str, source_id: str, source_type: str) -> str:
        """
        Inserts a new subscription into the MongoDB collection.

        Args:
            subscriber_id: The ID of the subscriber.
            source_id: The ID of the source.
            source_type: The type of the source.

        """
        subscription = {
            "subscriber_id": subscriber_id,
            "source_id": source_id,
            "source_type": source_type,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        result = self._collection.insert_one(subscription)
        return str(result.inserted_id)

    def update(self, subscriber_id: str, source_id: str, **kwargs: Any) -> int:
        """
        Updates an existing subscription in the MongoDB collection.

        Args:
            subscriber_id: The ID of the subscriber.
            source_id: The ID of the source.
            **kwargs: Additional fields to update.

        """
        filter_query = {
            "subscriber_id": subscriber_id,
            "source_id": source_id,
        }
        update_query = {"$set": kwargs, "$currentDate": {"updated_at": True}}
        result = self._collection.update_one(filter_query, update_query)
        return result.modified_count

    def get_subscription(
        self, subscriber_id: str, source_id: str
    ) -> Optional[dict[str, Any]]:
        """
        Retrieves a subscription from the MongoDB collection.

        Args:
            subscriber_id: The ID of the subscriber.
            source_id: The ID of the source.

        Returns:
            The subscription document if found, otherwise None.

        """
        filter_query = {
            "subscriber_id": subscriber_id,
            "source_id": source_id,
        }
        subscription = self._collection.find_one(filter_query)
        return subscription

    def delete_subscription(
        self, subscriber_id: str, source_id: str, source_type: Optional[str] = ""
    ) -> int:
        """
        Deletes a subscription from the MongoDB collection.

        Args:
            subscriber_id: The ID of the subscriber.
            source_id: The ID of the source.

        Returns:
            The number of deleted documents.

        """
        filter_query = {
            "subscriber_id": subscriber_id,
            "source_id": source_id,
        }
        if source_type:
            filter_query["source_type"] = source_type

        result = self._collection.delete_one(filter_query)
        return result.deleted_count
