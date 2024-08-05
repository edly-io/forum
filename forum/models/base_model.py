"""
Database models for forum.
"""

from abc import ABC, abstractmethod

from bson import ObjectId

from forum.mongo import MongoBackend


class MongoBaseModel(ABC):
    """Abstract Class for Mongo model implementation"""

    def __init__(self, collection_name=None, client=None):
        self.client = client or MongoBackend(collection=collection_name)

    @property
    def collection(self):
        """Get mongo db collection"""
        return self.client.collection

    @property
    def get_client(self):
        """Get mongo client"""
        return self.client

    def get(self, **kwargs):
        """Get a document by filter"""
        return self.collection.find_one(kwargs)

    def list(self, **kwargs):
        """Get a list of all documents filtered by kwargs"""
        return self.collection.find(kwargs)

    @abstractmethod
    def insert(self, **kwargs):
        """Insert a new document"""
        raise NotImplementedError

    def delete(self, _id: str):
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
    def update(self, _id: str, **kwargs):
        """Update a document by ID"""
        raise NotImplementedError
