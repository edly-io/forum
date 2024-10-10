"""Users Serializers class."""

from typing import Any

from rest_framework import serializers


class UserSerializer(serializers.Serializer[Any]):
    """Serializer for users."""

    id = serializers.CharField(allow_null=True)
    username = serializers.CharField()
    email = serializers.CharField(allow_null=True)
    external_id = serializers.CharField()
    subscribed_thread_ids = serializers.ListField(
        child=serializers.CharField(), default=[]
    )
    subscribed_commentable_ids = serializers.ListField(
        child=serializers.CharField(), default=[]
    )
    subscribed_user_ids = serializers.ListField(
        child=serializers.CharField(), default=[]
    )
    follower_ids = serializers.ListField(child=serializers.CharField(), default=[])
    upvoted_ids = serializers.ListField(child=serializers.CharField(), default=[])
    downvoted_ids = serializers.ListField(child=serializers.CharField(), default=[])
    default_sort_key = serializers.CharField(allow_null=True)

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError
