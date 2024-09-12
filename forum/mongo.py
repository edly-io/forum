"""Mongo module for forum app."""

import logging
from typing import Any, Optional

from django.conf import settings
from pymongo import MongoClient
from pymongo.database import Database as PymongoDatabase

log = logging.getLogger(__name__)

Database = PymongoDatabase[dict[str, Any]]


def get_database(
    database: Optional[str] = None,
    client_params: Optional[dict[Any, Any]] = None,
) -> Database:
    """
    Connect to MongoDB.

    :Parameters:

      - `database`: name of the mongodb database
      - `client_params`: parameters passed to MongoClient(...)
    """
    if database is None:
        database = settings.FORUM_MONGODB_DATABASE
    if client_params is None:
        client_params = settings.FORUM_MONGODB_CLIENT_PARAMETERS

    connection: MongoClient[Any] = MongoClient(**client_params)
    db = connection[database]
    return db
