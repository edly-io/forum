"""Users Serializers class."""

from typing import Any

from rest_framework import serializers


class UserSerializer(serializers.Serializer[Any]):
    """Serializer for users."""

    id = serializers.CharField(allow_null=True)
    username = serializers.CharField()
    external_id = serializers.CharField()
    subscribed_thread_ids = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    subscribed_commentable_ids = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    subscribed_user_ids = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    follower_ids = serializers.ListField(child=serializers.CharField(), allow_null=True)
    upvoted_ids = serializers.ListField(child=serializers.CharField(), allow_null=True)
    downvoted_ids = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    default_sort_key = serializers.CharField(allow_null=True)

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError
