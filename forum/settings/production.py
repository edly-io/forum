"""
Production settings for forum app.
"""


def plugin_settings(settings):  # type: ignore
    """
    Production settings for forum app
    """
    settings.FORUM_PORT = settings.ENV_TOKENS.get("FORUM_PORT", settings.FORUM_PORT)
    settings.MONGO_HOST = settings.ENV_TOKENS.get("MONGO_HOST", settings.MONGO_HOST)
    settings.MONGO_PORT = settings.ENV_TOKENS.get("MONGO_PORT", settings.MONGO_PORT)
