"""
Database models for forum.
"""

from abc import ABC, abstractmethod

from forum.mongo import MongoBackend


class AbstractModel(ABC):
    """Abstract Class for Mongo model implementation"""

    def __init__(self, collection_name):
        db_name = 'cs_comments_service'
        self.client = MongoBackend(collection=collection_name)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_collection(self):
        return self.collection

    def get_db(self):
        return self.db

    def get_client(self):
        return self.client

    @abstractmethod
    def get(self, id):
        pass
    
    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def insert(self, *kwargs):
        pass

    @abstractmethod
    def delete(self, id):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass
