"""
forum Django application initialization.
"""

from django.apps import AppConfig


class ForumConfig(AppConfig):
    """
    Configuration for the forum Django application.
    """

    name = "forum"

    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "forum",
                "regex": r"^forum/",
                "relative_path": "urls",
            }
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "devstack": {"relative_path": "settings.devstack"},
                "production": {"relative_path": "settings.production"},
            }
        },
    }

    def ready(self) -> None:
        """
        Import Signals.
        """
        import forum.signals  # pylint: disable=import-outside-toplevel, unused-import
