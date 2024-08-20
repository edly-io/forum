"""
Custom Serializer for the DataTime
"""

from datetime import datetime
from typing import Any

from rest_framework import serializers


class CustomDateTimeField(serializers.DateTimeField):
    """
    A custom DateTimeField serializer for formatting datetime objects in ISO 8601 format.
    """

    def to_representation(self, value: Any) -> str:
        """
        Convert the datetime object to an ISO 8601 formatted string with microseconds and UTC suffix.
        """
        # Check if the value is a datetime object
        if isinstance(value, datetime):
            # Format the datetime to ISO 8601 with microseconds and append 'Z'
            return f"{value:%Y-%m-%dT%H:%M}:{value.second:02}Z"

        # If the value is not a datetime object, fallback to the default representation
        return super().to_representation(value)
