"""
Production settings for forum app.
"""


def plugin_settings(settings):
    """
    Production settings for forum app
    """
    settings.FORUM_PORT = settings.ENV_TOKENS.get("FORUM_PORT", settings.FORUM_PORT)
