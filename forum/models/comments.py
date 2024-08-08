"""Comment Class for mongo backend."""

from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId

from forum.models.contents import Contents


class Comment(Contents):
    """
    Comment class for cs_comments_service content model
    """

    content_type = "Comment"

    def insert(
        self,
        body: str,
        course_id: str,
        comment_thread_id: str,
        author_id: str,
        author_username: str,
        anonymous: bool = False,
        anonymous_to_peers: bool = False,
        depth: int = 0,
    ):  # pylint: disable=arguments-differ
        """
        Inserts a new comment document into the database.

        Args:
            body (str): The body content of the comment.
            course_id (str): The ID of the course the comment is associated with.
            comment_thread_id (str): The ID of the parent comment thread.
            author_id (str): The ID of the author who created the comment.
            author_username (str): The username of the author.
            anonymous (bool, optional): Whether the comment is posted anonymously. Defaults to False.
            anonymous_to_peers (bool, optional): Whether the comment is anonymous to peers. Defaults to False.
            depth (int, optional): The depth of the comment in the thread hierarchy. Defaults to 0.

        Returns:
            str: The ID of the inserted document.
        """
        date = datetime.now()
        comment_data = {
            "votes": self.get_votes_dict(up=[], down=[]),
            "visible": True,
            "abuse_flaggers": [],
            "historical_abuse_flaggers": [],
            "parent_ids": [],
            "at_position_list": [],
            "body": body,
            "course_id": course_id,
            "_type": self.content_type,
            "endorsed": False,
            "anonymous": anonymous,
            "anonymous_to_peers": anonymous_to_peers,
            "author_id": author_id,
            "comment_thread_id": ObjectId(comment_thread_id),
            "child_count": 0,
            "depth": depth,
            "author_username": author_username,
            "created_at": date,
            "updated_at": date,
        }
        result = self.collection.insert_one(comment_data)
        return str(result.inserted_id)

    def update(
        self,
        comment_id: ObjectId,
        body: Optional[str] = None,
        course_id: Optional[str] = None,
        anonymous: Optional[bool] = None,
        anonymous_to_peers: Optional[bool] = None,
        comment_thread_id: Optional[ObjectId] = None,
        at_position_list: Optional[List[str]] = None,
        visible: Optional[bool] = None,
        author_id: Optional[str] = None,
        author_username: Optional[str] = None,
        votes: Optional[Dict[str, int]] = None,
        abuse_flaggers: Optional[List[str]] = None,
        endorsed: Optional[bool] = None,
        child_count: Optional[int] = None,
        depth: Optional[int] = None,
    ):  # pylint: disable=arguments-differ
        """
        Updates a comment document in the database.

        Args:
            comment_id (ObjectId): The ID of the comment to update.
            body (Optional[str], optional): The body content of the comment.
            course_id (Optional[str], optional): The ID of the course the comment is associated with.
            anonymous (Optional[bool], optional): Whether the comment is posted anonymously.
            anonymous_to_peers (Optional[bool], optional): Whether the comment is anonymous to peers.
            comment_thread_id (Optional[ObjectId], optional): The ID of the parent comment thread.
            at_position_list (Optional[List[str]], optional): A list of positions for @mentions.
            visible (Optional[bool], optional): Whether the comment is visible.
            author_id (Optional[str], optional): The ID of the author who created the comment.
            author_username (Optional[str], optional): The username of the author.
            votes (Optional[Dict[str, int]], optional): The votes for the comment.
            abuse_flaggers (Optional[List[str]], optional): A list of users who flagged the comment for abuse.
            endorsed (Optional[bool], optional): Whether the comment is endorsed.
            child_count (Optional[int], optional): The number of child comments.
            depth (Optional[int], optional): The depth of the comment in the thread hierarchy.

        Returns:
            int: The number of documents modified.
        """
        update_data = {}
        if body:
            update_data["body"] = body
        if course_id:
            update_data["course_id"] = course_id
        if anonymous is not None:
            update_data["anonymous"] = anonymous
        if anonymous_to_peers is not None:
            update_data["anonymous_to_peers"] = anonymous_to_peers
        if comment_thread_id:
            update_data["comment_thread_id"] = comment_thread_id
        if at_position_list:
            update_data["at_position_list"] = at_position_list
        if visible is not None:
            update_data["visible"] = visible
        if author_id:
            update_data["author_id"] = author_id
        if author_username:
            update_data["author_username"] = author_username
        if votes:
            update_data["votes"] = votes
        if abuse_flaggers:
            update_data["abuse_flaggers"] = abuse_flaggers
        if endorsed is not None:
            update_data["endorsed"] = endorsed
        if child_count is not None:
            update_data["child_count"] = child_count
        if depth is not None:
            update_data["depth"] = depth

        date = datetime.now()
        update_data["updated_at"] = date
        result = self.collection.update_one(
            {"_id": comment_id},
            {"$set": update_data},
        )
        return result.modified_count
