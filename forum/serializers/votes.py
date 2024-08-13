"""
Serializer for votes data.

Serializes the votes field in the ContentSerializer.
"""

from rest_framework import serializers


class VotesSerializer(serializers.Serializer):  # type: ignore
    """
    Serializer for votes data.

    Handles data of type dict[str, int].

    Attributes:
        up (list[str]): List of user IDs who upvoted the content.
        down (list[str]): List of user IDs who downvoted the content.
        up_count (int): Total number of upvotes.
        down_count (int): Total number of downvotes.
        count (int): Total number of votes.
        point (int): The point value of the content.
    """

    up = serializers.ListField(child=serializers.CharField())
    down = serializers.ListField(child=serializers.CharField())
    up_count = serializers.IntegerField()
    down_count = serializers.IntegerField()
    count = serializers.IntegerField()
    point = serializers.IntegerField()
