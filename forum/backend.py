"""Backend module for forum."""

from typing import Callable, Optional

from forum.backends.mongodb.api import MongoBackend
from forum.backends.mysql.api import MySQLBackend


def is_mysql_backend_enabled(course_id: str | None) -> bool:
    """
    Return True if mysql backend is enabled for the course.
    """
    try:
        from forum.toggles import ENABLE_MYSQL_BACKEND  # pylint: disable=C0415
    except ImportError:
        return True
    # pylint: disable=C0415,E0401
    from opaque_keys.edx.locator import CourseKey  # type: ignore[import-not-found]

    if isinstance(course_id, str):
        course_id = CourseKey.from_string(course_id)

    return ENABLE_MYSQL_BACKEND.is_enabled(course_id)


def get_backend(
    course_id: Optional[str] = None,
) -> Callable[[], MongoBackend | MySQLBackend]:
    """Return a factory function that lazily loads the backend API based on course_id."""

    def _get_backend() -> MongoBackend | MySQLBackend:
        if is_mysql_backend_enabled(course_id):
            return MySQLBackend()
        return MongoBackend()

    return _get_backend
