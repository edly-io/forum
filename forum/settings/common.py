"""
Common settings for forum app.
"""

from typing import Any


def plugin_settings(settings: Any) -> None:
    """
    Common settings for forum app
    Set these variables in the Tutor Config or lms.yml for local testing
    """
    settings.FORUM_PORT = "4567"
    settings.FORUM_MONGO_HOST = "mongodb"
    settings.FORUM_MONGO_PORT = 27017

    settings.FORUM_ELASTICSEARCH_INDEX_NAMES = ["comment_threads", "comments"]
    settings.FORUM_MAX_DEEP_SEARCH_COMMENT_COUNT = 1000

    settings.ELASTIC_SEARCH_CONFIG = [
        {
            "use_ssl": False,
            "host": "elasticsearch",
            "port": 9200,
        }
    ]
    settings.FORUM_ENABLE_ELASTIC_SEARCH = True
