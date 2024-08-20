"""
Serializer for the comment data.
"""

from typing import Any

from rest_framework import serializers

from forum.serializers.contents import EditHistorySerializer
from forum.serializers.votes import VoteSummarySerializer


class EndorsementSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for handling endorsement of a comment

    Attributes:
        user_id (str): The endorsement user id.
        time (datetime): The timestamp of when the user has endorsed the comment.
    """

    user_id = serializers.CharField()
    time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError


class CommentsAPISerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for handling user comment api calls.
    """

    id = serializers.CharField()
    user_id = serializers.CharField()
    thread_id = serializers.CharField()
    username = serializers.CharField()
    parent_id = serializers.CharField()
    endorsed = serializers.BooleanField(default=False)
    anonymous = serializers.BooleanField(default=False)
    anonymous_to_peers = serializers.BooleanField(default=False)
    closed = serializers.BooleanField(default=False)
    body = serializers.CharField()
    course_id = serializers.CharField()
    parent_id = serializers.CharField(default=None, allow_null=True)
    commentable_id = serializers.CharField(default="course")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    depth = serializers.IntegerField(default=0)
    abuse_flaggers = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    at_position_list = serializers.ListField(allow_null=True)
    type = serializers.CharField()
    child_count = serializers.IntegerField(default=0)
    votes = VoteSummarySerializer()
    edit_history = EditHistorySerializer(default=[], many=True)
    sk = serializers.SerializerMethodField()
    endorsement = EndorsementSerializer(default=None, required=False, allow_null=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        exclude_fields = kwargs.pop("exclude_fields", None)
        super().__init__(*args, **kwargs)
        if exclude_fields:
            for field in exclude_fields:
                self.fields.pop(field, None)

    def get_sk(self, obj: dict[str, Any]) -> str:
        """Return sk field"""
        is_child = obj.get("parent_id")
        if is_child is not None:
            return "{parent_id}-{id}".format(
                parent_id=obj.get("parent_id"), id=obj.get("_id")
            )
        else:
            return "{id}".format(id=obj.get("_id"))

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError
