"""
Vote Serializers
"""

from rest_framework import serializers


# pylint: disable=W0223
class VoteSerializer(serializers.Serializer):
    """
    Serializer for handling votes on a content item.

    Attributes:
        user_id (str): The ID of the user casting the vote.
        value (str): The value of the vote, either "up" or "down".
    """

    user_id = serializers.CharField(required=True)
    value = serializers.ChoiceField(choices=["up", "down"], required=True)


# pylint: disable=W0223
class VoteSummerySerializer(serializers.Serializer):
    """
    Serializer for summarizing votes on a content item.

    Attributes:
        count (int): The total number of votes.
        up_count (int): The number of upvotes.
        down_count (int): The number of downvotes.
        point (int): The net score (upvotes minus downvotes).
    """

    count = serializers.IntegerField(min_value=0)
    up_count = serializers.IntegerField(min_value=0)
    down_count = serializers.IntegerField(min_value=0)
    point = serializers.IntegerField()


# pylint: disable=W0223
class ContentSerializer(serializers.Serializer):
    """
    Serializer for handling the content of a post or comment.

    Attributes:
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
        votes (VoteSummerySerializer): A summary of votes on the content.
        abuse_flaggers (list): A list of user IDs who flagged the content as abusive.
        edit_history (list): A list of previous versions of the content.
        closed (bool): Whether the content is closed for further interactions.
        type (str): The type of content (e.g., "post", "comment").
    """

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
    votes = VoteSummerySerializer()
    abuse_flaggers = serializers.ListField(default=[])
    edit_history = serializers.ListField(default=[])
    closed = serializers.BooleanField(default=False)
    type = serializers.CharField()


# pylint: disable=W0223
class UserThreadSerializer(ContentSerializer):
    """
    Serializer for handling user-created threads.

    Inherits from ContentSerializer.

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
    context = serializers.CharField()
    last_activity_at = serializers.DateTimeField()
    closed_by = serializers.CharField(allow_null=True, default=None)
    tags = serializers.ListField(default=[])
    group_id = serializers.CharField(allow_null=True, default=None)
    pinned = serializers.BooleanField()
    comments_count = serializers.IntegerField(min_value=0, default=0)


# pylint: disable=W0223
class UserCommentSerializer(ContentSerializer):
    """
    Serializer for handling user comments on threads.

    Inherits from ContentSerializer.

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
