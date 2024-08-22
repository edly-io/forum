"""
Serializer for the comment data.
"""

from typing import Any

from rest_framework import serializers

from forum.serializers.contents import UserContentSerializer
from forum.serializers.custom_datetime import CustomDateTimeField


class EndorsementSerializer(serializers.Serializer[dict[str, Any]]):
    """
    Serializer for handling endorsement of a comment

    Attributes:
        user_id (str): The endorsement user id.
        time (datetime): The timestamp of when the user has endorsed the comment.
    """

    user_id = serializers.CharField()
    time = CustomDateTimeField()

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError


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
        sk (str or None): sk field, has ids data in it.
        endorsement: saves endorsement data.
    """

    endorsed = serializers.BooleanField(default=False)
    depth = serializers.IntegerField(default=0)
    thread_id = serializers.CharField()
    parent_id = serializers.CharField(default=None, allow_null=True)
    child_count = serializers.IntegerField(default=0)
    sk = serializers.SerializerMethodField()
    endorsement = EndorsementSerializer(default=None, required=False, allow_null=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        exclude_fields = kwargs.pop("exclude_fields", None)
        super().__init__(*args, **kwargs)
        if exclude_fields:
            for field in exclude_fields:
                self.fields.pop(field, None)

    def to_representation(self, instance: Any) -> dict[str, Any]:
        comment = super().to_representation(instance)
        if comment["parent_id"] == "None":
            comment["parent_id"] = None
        return comment

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
