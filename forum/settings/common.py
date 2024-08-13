"""
Common settings for forum app.
"""


def plugin_settings(settings):  # type: ignore
    """
    Common settings for forum app
    Set these variables in the Tutor Config or lms.yml for local testing
    """
    settings.FORUM_PORT = "4567"
    settings.MONGO_HOST = "mongodb"
    settings.MONGO_PORT = 27017
