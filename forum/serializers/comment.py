"""
Serializer for the comment data.
"""

import logging
from typing import Any

from bson import ObjectId
from rest_framework import serializers

from forum.models import Comment
from forum.serializers.contents import ContentSerializer
from forum.serializers.custom_datetime import CustomDateTimeField

log = logging.getLogger(__name__)


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


class CommentSerializer(ContentSerializer):
    """
    Serializer for handling user comments on threads.

    Inherits from ContentSerializer.

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
    thread_id = serializers.CharField(source="comment_thread_id")
    parent_id = serializers.CharField(default=None, allow_null=True)
    child_count = serializers.IntegerField(default=0)
    sk = serializers.SerializerMethodField()
    endorsement = EndorsementSerializer(default=None, required=False, allow_null=True)
    children = serializers.SerializerMethodField()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        exclude_fields = kwargs.pop("exclude_fields", None)
        context = kwargs.pop("context", {})
        self.recursive = context.pop("recursive", False)
        super().__init__(*args, **kwargs)
        if exclude_fields:
            for field in exclude_fields:
                self.fields.pop(field, None)

    def get_children(self, obj: Any) -> list[dict[str, Any]]:
        if self.recursive:
            children = list(
                Comment().list(
                    parent_id=ObjectId(obj["_id"]),
                    depth=1,
                )
            )
            children_data = []
            for child in children:
                children_data.append(
                    {
                        **child,
                        "id": str(child.get("_id")),
                        "user_id": child.get("author_id"),
                        "thread_id": str(child.get("comment_thread_id")),
                        "username": child.get("author_username"),
                        "parent_id": str(child.get("parent_id")),
                        "type": str(child.get("_type", "")).lower(),
                    }
                )
            serializer = CommentSerializer(
                children_data,
                many=True,
                context={"recursive": False},
                exclude_fields={"sk"},
            )
            return serializer.data
        return []

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
