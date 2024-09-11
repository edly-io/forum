"""
Production settings for forum app.
"""

from typing import Any


def plugin_settings(settings: Any) -> None:
    """
    Production settings for forum app.
    """
    settings.FORUM_PORT = settings.ENV_TOKENS.get("FORUM_PORT", settings.FORUM_PORT)
    settings.FORUM_MONGO_HOST = settings.ENV_TOKENS.get(
        "FORUM_MONGO_HOST", getattr(settings, "MONGO_HOST", "mongodb")
    )
    settings.FORUM_MONGO_PORT = settings.ENV_TOKENS.get(
        "FORUM_MONGO_PORT", getattr(settings, "MONGO_PORT", 27017)
    )
    settings.ELASTIC_SEARCH_CONFIG = settings.ENV_TOKENS.get(
        "ELASTIC_SEARCH_CONFIG", settings.ELASTIC_SEARCH_CONFIG
    )
    settings.FORUM_ENABLE_ELASTIC_SEARCH = settings.ENV_TOKENS.get(
        "FORUM_ENABLE_ELASTIC_SEARCH", settings.FORUM_ENABLE_ELASTIC_SEARCH
    )
