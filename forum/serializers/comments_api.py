"""
Serializer for the comment data.
"""

from rest_framework import serializers

from forum.models.comments import Comment
from forum.serializers.contents import EditHistorySerializer
from forum.serializers.votes import VoteSummarySerializer


class EndorsementSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")


class CommentsAPICommonSerializer(serializers.Serializer):
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

    def get_sk(self, obj):
        is_child = True if obj.get("parent_id") else False
        if is_child:
            return "{parent_id}-{id}".format(
                parent_id=obj.get("parent_id"), id=obj.get("_id")
            )
        else:
            return "{id}".format(id=obj.get("_id"))


class CommentsAPIGetSerializer(CommentsAPICommonSerializer):
    """
    Serializer for handling user comment get api calls.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("sk", None)


class CommentsAPIPostAndDeleteSerializer(CommentsAPICommonSerializer):
    """
    Serializer for handling user comment post and delete api calls.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("sk", None)
        self.fields.pop("endorsement", None)
