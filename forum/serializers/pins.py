"""
Pin/Unpin threads Serializers
"""

from bson import ObjectId
from rest_framework import serializers

from forum.models.comments import Comment
from forum.serializers.votes import UserThreadSerializer


class PinUnpinThreadSerializer(UserThreadSerializer):
    """
    Serializer for handling pin/unpin threads.

    Inherits from UserThreadSerializer.

    Attributes:
        id (str): The ID of the thread.
        comments_count (int): The number of comments belongs to the thread.
    """

    id = serializers.CharField()
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        count = len(list(Comment().list(comment_thread_id=ObjectId(obj.get("id")))))
        return count
