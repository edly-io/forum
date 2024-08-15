"""
Serializer for the thread data.
"""

from typing import Any, Dict

from rest_framework import serializers

from forum.models.model_utils import get_comments_count
from forum.serializers.contents import UserContentSerializer


class UserThreadSerializer(UserContentSerializer):
    """
    Serializer for handling user-created threads.

    Inherits from UserContentSerializer.

    Attributes:
        thread_type (str): The type of thread (e.g., "discussion", "question").
        title (str): The title of the thread.
        context (str): The context or additional description of the thread.
        last_activity_at (datetime): The timestamp of the last activity in the thread.
        closed_by (str or None): The user who closed the thread, if any.
        tags (list): A list of tags associated with the thread.
        group_id (str or None): The ID of the group associated with the thread, if any.
        pinned (bool): Whether the thread is pinned at the top of the list.
        comments_count (int): The number of comments on the thread.
    """

    thread_type = serializers.CharField()
    title = serializers.CharField()
    context = serializers.CharField()  # type: ignore
    last_activity_at = serializers.DateTimeField()
    closed_by = serializers.CharField(allow_null=True, default=None)
    tags = serializers.ListField(default=[])
    group_id = serializers.CharField(allow_null=True, default=None)
    pinned = serializers.BooleanField()
    comments_count = serializers.SerializerMethodField()

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def get_comments_count(self, obj: Dict[str, Any]) -> int:
        count = get_comments_count(obj["id"])
        return count
