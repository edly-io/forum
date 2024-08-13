"""Serializer class for content collection."""

from typing import Any, Dict

from rest_framework import serializers

from forum.serializers.votes import VotesSerializer, VoteSummarySerializer


class EditHistorySerializer(serializers.Serializer):  # type: ignore
    """
    Serializer for handling edit history of a post or comment

    Attributes:
        original_body (str): The original content of the post or comment before the edit.
        reason_code (str): The code representing the reason for editing the post or comment.
        editor_username (str): The username of the person who made the edit.
        created_at (datetime): The timestamp of when the edit was made.
    """

    original_body = serializers.CharField()
    reason_code = serializers.CharField(allow_null=True, default=None)
    editor_username = serializers.CharField()
    created_at = serializers.DateTimeField()

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError


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
    abuse_flaggers = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
    historical_abuse_flaggers = serializers.ListField(
        child=serializers.CharField(), allow_null=True
    )
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

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError


class UserContentSerializer(serializers.Serializer):  # type: ignore
    """
    Serializer for handling the content of a post or comment.

    Attributes:
        id (str): The ID of the Content.
        body (str): The main content text.
        course_id (str): The ID of the related course.
        anonymous (bool): Whether the content is posted anonymously.
        anonymous_to_peers (bool): Whether the content is anonymous to peers.
        created_at (datetime): The timestamp when the content was created.
        updated_at (datetime): The timestamp when the content was last updated.
        at_position_list (list): A list of positions where @mentions occur.
        user_id (str): The ID of the user who created the content.
        username (str): The username of the content creator.
        commentable_id (str): The ID of the entity the content is related to (e.g., course).
        votes (VoteSummarySerializer): A summary of votes on the content.
        abuse_flaggers (list): A list of user IDs who flagged the content as abusive.
        edit_history (list): A list of previous versions of the content.
        closed (bool): Whether the content is closed for further interactions.
        type (str): The type of content (e.g., "post", "comment").
    """

    id = serializers.CharField()
    body = serializers.CharField()
    course_id = serializers.CharField()
    anonymous = serializers.BooleanField(default=False)
    anonymous_to_peers = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    at_position_list = serializers.ListField(default=[])
    user_id = serializers.CharField()
    username = serializers.CharField()
    commentable_id = serializers.CharField(default="course")
    votes = VoteSummarySerializer()
    abuse_flaggers = serializers.ListField(default=[])
    edit_history = EditHistorySerializer(default=[], many=True)
    closed = serializers.BooleanField(default=False)
    type = serializers.CharField()

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> Any:
        """Raise NotImplementedError"""
        raise NotImplementedError
