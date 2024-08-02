# serializers.py
from rest_framework import serializers

class EditHistorySerializer(serializers.Serializer):
    field_name = serializers.CharField()
    old_value = serializers.CharField()
    new_value = serializers.CharField()
    edited_at = serializers.DateTimeField()

class VoteSerializer(serializers.Serializer):
    count = serializers.IntegerField(default=0)
    up_count = serializers.IntegerField(default=0)
    down_count = serializers.IntegerField(default=0)
    point = serializers.IntegerField(default=0)

class CommentThreadSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', read_only=True)
    thread_type = serializers.CharField()
    title = serializers.CharField()
    body = serializers.CharField()
    course_id = serializers.CharField()
    anonymous = serializers.BooleanField()
    anonymous_to_peers = serializers.BooleanField()
    commentable_id = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    at_position_list = serializers.ListField(child=serializers.CharField(), default=[])
    closed = serializers.BooleanField()
    context = serializers.CharField()
    last_activity_at = serializers.DateTimeField()
    user_id = serializers.CharField(source='author_id')
    username = serializers.CharField(source='author_username')
    votes = VoteSerializer()
    abuse_flaggers = serializers.ListField(child=serializers.CharField(), default=[])
    edit_history = EditHistorySerializer(many=True, default=[])
    closed_by = serializers.SerializerMethodField()
    tags = serializers.ListField(child=serializers.CharField(), default=[])
    type = serializers.CharField(default='thread')
    group_id = serializers.CharField(allow_null=True)
    pinned = serializers.BooleanField(default=False)
    comments_count = serializers.IntegerField(source='comment_count')
    read = serializers.BooleanField(default=True)
    unread_comments_count = serializers.IntegerField(default=0)
    endorsed = serializers.BooleanField(default=False)
    
    def get_closed_by(self, obj):
        if hasattr(obj, 'closed_by') and obj.closed_by:
            return obj.closed_by.username
        return None
