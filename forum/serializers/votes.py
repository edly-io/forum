"""Serializer for votes data."""
from rest_framework import serializers


class VotesSerializer(serializers.Serializer):
    """
    Serializer for the votes field in the ContentSerializer.

    Attributes:
        up (ListField): List of user IDs who upvoted the content.
        down (ListField): List of user IDs who downvoted the content.
        up_count (IntegerField): Total number of upvotes.
        down_count (IntegerField): Total number of downvotes.
        count (IntegerField): Total number of votes.
        point (IntegerField): The point value of the content.
    """
    up = serializers.ListField(child=serializers.CharField())
    down = serializers.ListField(child=serializers.CharField())
    up_count = serializers.IntegerField()
    down_count = serializers.IntegerField()
    count = serializers.IntegerField()
    point = serializers.IntegerField()
