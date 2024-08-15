"""
Database models for forum.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from bson import ObjectId
from pymongo.collection import Collection as PymongoCollection
from pymongo.cursor import Cursor

from forum.mongo import Database, get_database

Collection = PymongoCollection[dict[str, Any]]


class MongoBaseModel(ABC):
    """Abstract Class for Mongo model implementation"""

    MONGODB_DATABASE: Optional[Database] = None
    COLLECTION_NAME: str = "default"

    @property
    def _collection(self) -> Collection:
        return self.__get_database()[self.COLLECTION_NAME]

    @classmethod
    def __get_database(cls) -> Database:
        """Get or create static class database."""
        if cls.MONGODB_DATABASE is None:
            cls.MONGODB_DATABASE = get_database()
        return cls.MONGODB_DATABASE

    def get(self, _id: str) -> Optional[dict[str, Any]]:
        """Get a document by filter"""
        return self._collection.find_one({"_id": _id})

    def list(self, **kwargs: Any) -> Cursor[dict[str, Any]]:
        """Get a list of all documents filtered by kwargs"""
        return self._collection.find(kwargs)

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
        result = self._collection.delete_one({"_id": ObjectId(_id)})
        return result.deleted_count

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> int:
        """Update a document by ID"""
        raise NotImplementedError
