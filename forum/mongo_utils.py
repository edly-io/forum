"""
Utility functions for extracting data from the MongoDB.
"""

from forum.models import Contents


def update_vote(content, user, vote_type=None, is_deleted=False):
    """
    Update a vote on a thread (either upvote or downvote).

    :param content: The content document containing vote data.
    :param user: The user document for the user voting.
    :param vote_type: String indicating the type of vote ('up' or 'down').
    :param is_deleted: Boolean indicating if the user is removing their vote (True) or voting (False).
    :return: The updated vote count or 0 if no update was made.
    """
    user_id = user["_id"]
    content_id = content["_id"]
    votes = content["votes"]

    update_needed = False

    if not is_deleted:
        if vote_type not in ["up", "down"]:
            raise ValueError("Invalid vote_type, use ('up' or 'down')")

        if vote_type == "up":
            current_votes = set(votes["up"])
            opposite_votes = set(votes["down"])
        else:
            current_votes = set(votes["down"])
            opposite_votes = set(votes["up"])

        # Check if user is voting
        if user_id not in current_votes:
            current_votes.add(user_id)
            update_needed = True
            if user_id in opposite_votes:
                opposite_votes.remove(user_id)

        updated_up_votes = (
            list(opposite_votes) if vote_type == "down" else list(current_votes)
        )
        updated_down_votes = (
            list(current_votes) if vote_type == "down" else list(opposite_votes)
        )

    else:
        # Handle vote deletion
        updated_up_votes = set(votes["up"])
        updated_down_votes = set(votes["down"])

        if user_id in updated_up_votes:
            updated_up_votes.remove(user_id)
            update_needed = True
        if user_id in updated_down_votes:
            updated_down_votes.remove(user_id)
            update_needed = True

    if update_needed:
        # Prepare updated votes
        content_model = Contents()
        updated_votes = content_model.get_votes_dict(
            updated_up_votes, updated_down_votes
        )
        updated_count = content_model.update_votes(
            content_id=content_id, votes=updated_votes
        )
        return updated_count

    return 0


def upvote_content(thread, user):
    """
    Upvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be upvoted.
        user (dict): The user who is performing the upvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(thread, user, vote_type="up")


def downvote_content(thread, user):
    """
    Downvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be downvoted.
        user (dict): The user who is performing the downvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(thread, user, vote_type="down")


def remove_vote(thread, user):
    """
    Remove the vote (upvote or downvote) from the specified thread or comment for the given user.

    Args:
        thread (dict): The thread or comment data from which the vote should be removed.
        user (dict): The user who is removing their vote.

    Returns:
        bool: True if the vote was successfully removed, False otherwise.
    """
    return update_vote(thread, user, is_deleted=True)
