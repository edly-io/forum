"""Backend module for forum."""

from typing import Callable, Optional

from forum.backends.mongodb.api import MongoBackend
from forum.backends.mysql.api import MySQLBackend


def get_backend(
    course_id: Optional[str] = "",
) -> Callable[[], MongoBackend | MySQLBackend]:
    """Return a factory function that lazily loads the backend API based on course_id."""

    def _get_backend() -> MongoBackend | MySQLBackend:
        if not course_id:
            # Lazy loading MongoBackend
            return MongoBackend()
        # TODO: add condition for course waffle flag.
        # Lazy loading MySQLBackend
        return MySQLBackend()

    return _get_backend
