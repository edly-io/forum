"""
Database models for forum.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor

from forum.mongo import MongoBackend


class MongoBaseModel(ABC):
    """Abstract Class for Mongo model implementation"""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        client: Optional[MongoBackend] = None,
    ) -> None:
        self.client: MongoBackend = client or MongoBackend(collection=collection_name)

    @property
    def collection(self) -> Collection[Dict[str, Any]]:
        """Get mongo db collection"""
        return self.client.collection

    @property
    def get_client(self) -> MongoBackend:
        """Get mongo client"""
        return self.client

    def get(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Get a document by filter"""
        return self.collection.find_one(kwargs)

    def list(self, **kwargs: Any) -> Cursor[Dict[str, Any]]:
        """Get a list of all documents filtered by kwargs"""
        return self.collection.find(kwargs)

    @abstractmethod
    def insert(self, *args: Any, **kwargs: Any) -> str:
        """Insert a new document"""
        raise NotImplementedError

    def delete(self, _id: str) -> int:
        """
        Deletes a document from the database based on the id.

        Args:
            _id: The ID of the document.

        Returns:
            The number of documents deleted.
        """
        result = self.collection.delete_one({"_id": ObjectId(_id)})
        return result.deleted_count

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> int:
        """Update a document by ID"""
        raise NotImplementedError
