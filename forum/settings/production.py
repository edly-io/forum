"""
Production settings for forum app.
"""

from typing import Any


def plugin_settings(settings: Any) -> None:
    """
    Production settings for forum app
    """
    settings.FORUM_PORT = settings.ENV_TOKENS.get("FORUM_PORT", settings.FORUM_PORT)
    settings.MONGO_HOST = settings.ENV_TOKENS.get("MONGO_HOST", settings.MONGO_HOST)
    settings.MONGO_PORT = settings.ENV_TOKENS.get("MONGO_PORT", settings.MONGO_PORT)

    settings.ELASTIC_SEARCH_CONFIG = settings.ENV_TOKENS.get(
        "ELASTIC_SEARCH_CONFIG", settings.ELASTIC_SEARCH_CONFIG
    )
