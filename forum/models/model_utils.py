"""Model util function for db operations."""

from typing import Any, Dict, Union

from forum.models.contents import Contents
from forum.models.users import Users


def flag_as_abuse(user: Dict[str, Any], entity: Dict[str, Any]) -> Union[Dict[str, Any], None]:
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


def un_flag_as_abuse(user: Dict[str, Any], entity: Dict[str, Any]) -> Union[Dict[str, Any], None]:
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
