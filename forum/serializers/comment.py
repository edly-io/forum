"""
Serializer for the comment data.
"""
from typing import Any, Dict

from rest_framework import serializers

from forum.serializers.contents import UserContentSerializer


class UserCommentSerializer(UserContentSerializer):
    """
    Serializer for handling user comments on threads.

    Inherits from UserContentSerializer.

    Attributes:
        endorsed (bool): Whether the comment is endorsed by an authority.
        depth (int): The depth of the comment in a nested comment structure.
        thread_id (str): The ID of the thread the comment belongs to.
        parent_id (str or None): The ID of the parent comment, if any.
        child_count (int): The number of child comments nested under this comment.
    """

    endorsed = serializers.BooleanField(default=False)
    depth = serializers.IntegerField(default=0)
    thread_id = serializers.CharField()
    parent_id = serializers.CharField(default=None)
    child_count = serializers.IntegerField(default=0)

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError
