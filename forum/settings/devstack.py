"""
Development settings for forum app.
"""

from typing import Any

from .common import plugin_settings as common_plugin_settings


def plugin_settings(settings: Any) -> None:
    """
    Production settings for forum app.

    For now there are no custom production settings. Add settings here if we need to
    override common settings.
    """
    common_plugin_settings(settings)
