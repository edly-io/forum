"""Mongo module for forum app."""

import logging
from typing import Any, Optional

from django.conf import settings
from pymongo import MongoClient
from pymongo.database import Database as PymongoDatabase

log = logging.getLogger(__name__)

Database = PymongoDatabase[dict[str, Any]]


def get_database(
    host: str = settings.FORUM_MONGO_HOST,
    port: int = settings.FORUM_MONGO_PORT,
    user: str = "",
    password: str = "",
    database: str = "cs_comments_service",
    authsource: Optional[str] = None,
    tz_aware: bool = True,
    **extra: Any
) -> Database:
    """
    Connect to MongoDB.

    :Parameters:

      - `host`: hostname
      - `port`: port
      - `user`: collection username
      - `password`: collection user password
      - `database`: name of the database
      - `authsource`: name of the authentication database
      - `extra`: parameters to pymongo.MongoClient not listed above

    """
    connection: MongoClient[Any] = MongoClient(
        host=host, port=port, tz_aware=tz_aware, **extra
    )
    db = connection[database]

    if user or password:
        db.authenticate(user, password, source=authsource)

    return db
