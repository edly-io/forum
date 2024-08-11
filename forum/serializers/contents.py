"""Serializer class for content collection."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rest_framework import serializers

from forum.serializers.votes import VotesSerializer


class ContentSerializer(serializers.Serializer[Dict[str, Any]]):
    """
    Serializer for the content data.

    Attributes:
        _id (CharField): The ID of the content.
        votes (VotesSerializer): The votes data for the content.
        visible (BooleanField): Whether the content is visible.
        abuse_flaggers (ListField): List of user IDs who flagged the content for abuse.
        historical_abuse_flaggers (ListField): List of user IDs who historically flagged the content for abuse.
        parent_ids (ListField): List of parent IDs for the content.
        at_position_list (ListField): List of positions for the content.
        body (CharField): The body text of the content.
        course_id (CharField): The ID of the course associated with the content.
        _type (CharField): The type of content.
        endorsed (BooleanField): Whether the content is endorsed.
        anonymous (BooleanField): Whether the content is anonymous.
        anonymous_to_peers (BooleanField): Whether the content is anonymous to peers.
        parent_id (CharField): The ID of the parent content.
        author_id (CharField): The ID of the author of the content.
        comment_thread_id (CharField): The ID of the comment thread associated with the content.
        child_count (IntegerField): The number of child comments.
        depth (IntegerField): The depth of the content in the comment thread.
        author_username (CharField): The username of the author of the content.
        sk (CharField): The sorting key for the content.
        updated_at (DateTimeField): The date and time the content was last updated.
        created_at (DateTimeField): The date and time the content was created.
    """

    _id = serializers.CharField()
    votes = VotesSerializer(allow_null=True)
    visible = serializers.BooleanField(allow_null=True)
    abuse_flaggers = serializers.ListField(child=serializers.CharField(), allow_null=True)
    historical_abuse_flaggers = \
        serializers.ListField(child=serializers.CharField(), allow_null=True)
    parent_ids = serializers.ListField(child=serializers.CharField(), allow_null=True)
    at_position_list = serializers.ListField(allow_null=True)
    body = serializers.CharField(allow_null=True)
    course_id = serializers.CharField(allow_null=True)
    _type = serializers.CharField(allow_null=True)
    endorsed = serializers.BooleanField(allow_null=True)
    anonymous = serializers.BooleanField(allow_null=True)
    anonymous_to_peers = serializers.BooleanField(allow_null=True)
    parent_id = serializers.CharField(allow_null=True)
    author_id = serializers.CharField(allow_null=True)
    comment_thread_id = serializers.CharField(allow_null=True)
    child_count = serializers.IntegerField(allow_null=True)
    depth = serializers.IntegerField(allow_null=True)
    author_username = serializers.CharField(allow_null=True)
    sk = serializers.CharField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
