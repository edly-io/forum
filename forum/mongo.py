"""Mongo module for forum app."""

import logging
from typing import Any, Dict

from django.conf import settings
from pymongo import MongoClient
from pymongo.collection import Collection

log = logging.getLogger(__name__)


class MongoBackend:
    """Class for mongoDB cs_comments_service backend."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Connect to MongoDB.

        :Parameters:

          - `host`: hostname
          - `port`: port
          - `user`: collection username
          - `password`: collection user password
          - `database`: name of the database
          - `collection`: name of the collection
          - `authsource`: name of the authentication database
          - `extra`: parameters to pymongo.MongoClient not listed above

        """
        # Extract connection parameters from kwargs

        host = kwargs.get("host", settings.MONGO_HOST)
        port = kwargs.get("port", settings.MONGO_PORT)

        user = kwargs.get("user", "")
        password = kwargs.get("password", "")

        db_name = kwargs.get("database", "cs_comments_service")
        collection_name = kwargs.get("collection", "")

        auth_source = kwargs.get("authsource") or None

        # Other mongo connection arguments
        extra = kwargs.get("extra", {})

        # Make timezone aware by default
        extra["tz_aware"] = extra.get("tz_aware", True)

        # Connect to database and get collection

        self.connection: MongoClient[Any] = MongoClient(host=host, port=port, **extra)

        database = self.connection[db_name]

        if user or password:
            database.authenticate(user, password, source=auth_source)

        self.collection: Collection[Dict[str, Any]] = database[collection_name]
