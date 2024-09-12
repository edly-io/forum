"""
Common settings for forum app.
"""

from typing import Any


def plugin_settings(settings: Any) -> None:
    """
    Common settings for forum app
    """
    settings.FORUM_MONGODB_DATABASE = "cs_comments_service"
    settings.FORUM_ENABLE_ELASTIC_SEARCH = True

    # Unfortunately we can't copy settings from edx-platform because tutor patches have
    # not been applied yet
    settings.FORUM_MONGODB_CLIENT_PARAMETERS = getattr(
        settings, "FORUM_MONGODB_CLIENT_PARAMETERS", {"host": "mongodb"}
    )
    settings.FORUM_ELASTIC_SEARCH_CONFIG = getattr(
        settings, "FORUM_ELASTIC_SEARCH_CONFIG", [{"host": "elasticsearch"}]
    )

    # Enable forum service
    settings.FEATURES["ENABLE_DISCUSSION_SERVICE"] = True
    # URL prefix must match the regex in the url_config of the plugin app
    settings.COMMENTS_SERVICE_URL = "http://localhost:8000/forum"
