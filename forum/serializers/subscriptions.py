"""Serializer for Subscriptions."""

from typing import Any

from rest_framework import serializers


class SubscriptionSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for Subscription data.

    This serializer is used to serialize and deserialize subscription data.
    """

    id = serializers.CharField(source="_id")
    subscriber_id = serializers.CharField()
    source_id = serializers.CharField()
    source_type = serializers.CharField()

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError
