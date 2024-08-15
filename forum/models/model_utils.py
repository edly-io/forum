"""Model util function for db operations."""

from typing import Any, Dict, Tuple, Union

from forum.models import Comment, CommentThread, Contents, Users


def flag_as_abuse(
    user: Dict[str, Any], entity: Dict[str, Any]
) -> Union[Dict[str, Any], None]:
    """
    Flag an entity as abuse.

    Args:
        user (Dict[str, Any]): The user who is flagging the entity as abuse.
        entity (Dict[str, Any]): The entity being flagged as abuse.

    Returns:
        Dict[str, Any]: The updated entity with the abuse flag.

    Raises:
        ValueError: If user ID or entity is not provided.
    """

    abuse_flaggers = entity["abuse_flaggers"]
    if user["_id"] not in abuse_flaggers:
        abuse_flaggers.append(user["_id"])
        Contents().update(
            entity["_id"],
            abuse_flaggers=abuse_flaggers,
        )

    # Check if this is the first abuse flag
    first_flag_added = len(entity["abuse_flaggers"]) == 1

    # If this is the first abuse flag, update author's stats
    active_flags = user.get("active_flags", 0) + 1
    if first_flag_added:
        Users().update(
            entity["author_id"],
            active_flags=active_flags,
        )

    # Reload the object and return it as a JSON string
    return Contents().get(entity["_id"])


def un_flag_as_abuse(
    user: Dict[str, Any], entity: Dict[str, Any]
) -> Union[Dict[str, Any], None]:
    """
    Unflag an entity as abuse.

    Args:
        user (Dict[str, Any]): The user who is unflagging the entity as abuse.
        entity (Dict[str, Any]): The entity being unflagged as abuse.

    Returns:
        Dict[str, Any]: The updated entity with the abuse flag removed.

    Raises:
        ValueError: If user ID or entity is not provided.
    """
    if user["_id"] in entity["abuse_flaggers"]:
        entity["abuse_flaggers"].remove(user["_id"])
        Contents().update(
            entity["_id"],
            abuse_flaggers=entity["abuse_flaggers"],
        )
    # TODO: Update course stats for abuse.
    return Contents().get(entity["_id"])


def un_flag_all_as_abuse(entity: Dict[str, Any]) -> Union[Dict[str, Any], None]:
    """
    Unflag an entity as abuse for all users.

    Args:
        entity (Dict[str, Any]): The entity being unflagged as abuse.

    Returns:
        Dict[str, Any]: The updated entity with all abuse flags removed.

    Raises:
        ValueError: If entity is not provided.
    """
    Contents().update(entity["_id"], abuse_flaggers=[])
    # TODO: Update course stats for abuse.
    return Contents().get(entity["_id"])


def update_vote(
    content: Dict[str, Any],
    user: Dict[str, Any],
    vote_type: str = "",
    is_deleted: bool = False,
) -> bool:
    """
    Update a vote on a thread (either upvote or downvote).

    :param content: The content document containing vote data.
    :param user: The user document for the user voting.
    :param vote_type: String indicating the type of vote ('up' or 'down').
    :param is_deleted: Boolean indicating if the user is removing their vote (True) or voting (False).
    :return: True if the vote was successfully updated, False otherwise.
    """
    user_id: str = user["_id"]
    content_id: str = str(content["_id"])
    votes: Dict[str, Any] = content["votes"]

    update_needed: bool = False

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

        updated_up_votes = opposite_votes if vote_type == "down" else current_votes
        updated_down_votes = current_votes if vote_type == "down" else opposite_votes

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
            list(updated_up_votes), list(updated_down_votes)
        )
        updated_count = content_model.update_votes(
            content_id=content_id, votes=updated_votes
        )
        return bool(updated_count)

    return False


def upvote_content(thread: Dict[str, Any], user: Dict[str, Any]) -> bool:
    """
    Upvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be upvoted.
        user (dict): The user who is performing the upvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(thread, user, vote_type="up")


def downvote_content(thread: Dict[str, Any], user: Dict[str, Any]) -> bool:
    """
    Downvotes the specified thread or comment by the given user.

    Args:
        thread (dict): The thread or comment data to be downvoted.
        user (dict): The user who is performing the downvote.

    Returns:
        bool: True if the vote was successfully updated, False otherwise.
    """
    return update_vote(thread, user, vote_type="down")


def remove_vote(thread: Dict[str, Any], user: Dict[str, Any]) -> bool:
    """
    Remove the vote (upvote or downvote) from the specified thread or comment for the given user.

    Args:
        thread (dict): The thread or comment data from which the vote should be removed.
        user (dict): The user who is removing their vote.

    Returns:
        bool: True if the vote was successfully removed, False otherwise.
    """
    return update_vote(thread, user, is_deleted=True)


def get_comments_count(thread_id: str) -> int:
    """
    Returns that comments count in a perticular thread
    """
    comments = list(Comment().list(comment_thread_id=thread_id))
    return len(comments) if comments else 0


def validate_thread_and_user(
    user_id: str, thread_id: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Validate thread and user.

    Arguments:
        user_id (str): The ID of the user making the request.
        thread_id (str): The ID of the thread.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: A tuple containing the user and thread data.

    Raises:
        ValueError: If the thread or user is not found.
    """
    thread = CommentThread().get(thread_id)
    user = Users().get(user_id)
    if not (thread and user):
        raise ValueError("User / Thread doesn't exist")

    return user, thread


def pin_unpin_thread(thread_id: str, action: str) -> None:
    """
    Pin or unpin the thread based on action parameter.

    Arguments:
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").
    """
    CommentThread().update(thread_id, pinned=action == "pin")


def get_pinned_unpinned_thread_serialized_data(
    user: Dict[str, Any], thread_id: str, serializer_class: Any
) -> Dict[str, Any]:
    """
    Return serialized data of pinned or unpinned thread.

    Arguments:
        user (Dict[str, Any]): The user who requested the action.
        thread_id (str): The ID of the thread to pin/unpin.

    Returns:
        Dict[str, Any]: The serialized data of the pinned/unpinned thread.

    Raises:
        ValueError: If the serialization is not valid.
    """
    updated_thread = CommentThread().get(thread_id)
    context = {
        "user_id": user["_id"],
        "username": user["username"],
        "type": "thread",
        "id": thread_id,
    }
    if updated_thread is not None:
        context = {**context, **updated_thread}
    serializer = serializer_class(data=context)
    if not serializer.is_valid():
        raise ValueError(serializer.errors)

    return serializer.data


def handle_pin_unpin_thread_request(
    user_id: str, thread_id: str, action: str, serializer_class: Any
) -> Dict[str, Any]:
    """
    Catches pin/unpin thread request.

    - validates thread and user.
    - pin or unpin the thread based on action parameter.
    - return serialized data of thread.

    Arguments:
        user_id (str): The ID of the user making the request.
        thread_id (str): The ID of the thread to pin/unpin.
        action (str): The action to perform ("pin" or "unpin").

    Returns:
        Dict[str, Any]: The serialized data of the pinned/unpinned thread.
    """
    user, _ = validate_thread_and_user(user_id, thread_id)
    pin_unpin_thread(thread_id, action)
    return get_pinned_unpinned_thread_serialized_data(user, thread_id, serializer_class)
