"""Content Class for mongo backend."""

from datetime import datetime
from typing import Dict, List, Optional

from forum.models.contents import Contents


class CommentThread(Contents):
    """
    CommentThread class for cs_comments_service content model
    """

    content_type = "CommentThread"

    def get_votes(self, up=None, down=None):
        """
        Calculates and returns the vote summary for a thread.

        Args:
            up (list, optional): A list of user IDs who upvoted the thread.
            down (list, optional): A list of user IDs who downvoted the thread.

        Returns:
            dict: A dictionary containing the vote summary with the following keys:
                - "up" (list): The list of user IDs who upvoted.
                - "down" (list): The list of user IDs who downvoted.
                - "up_count" (int): The count of upvotes.
                - "down_count" (int): The count of downvotes.
                - "count" (int): The total number of votes (upvotes + downvotes).
                - "point" (int): The vote score (upvotes - downvotes).
        """
        up = up or []
        down = down or []
        votes = {
            "up": up,
            "down": down,
            "up_count": len(up),
            "down_count": len(down),
            "count": len(up) + len(down),
            "point": len(up) - len(down),
        }
        return votes

    def insert(
        self,
        title: str,
        body: str,
        course_id: str,
        commentable_id: str,
        author_id: str,
        author_username: str,
        anonymous: bool = False,
        anonymous_to_peers: bool = False,
        thread_type: str = "discussion",
        context: str = "course",
    ):  # pylint: disable=arguments-differ
        """
        Inserts a new thread document into the database.

        Args:
            title (str): The title of the thread.
            body (str): The body content of the thread.
            course_id (str): The ID of the course the thread is associated with.
            commentable_id (str): The ID of the commentable entity.
            author_id (str): The ID of the author who created the thread.
            author_username (str): The username of the author.
            anonymous (bool, optional): Whether the thread is posted anonymously. Defaults to False.
            anonymous_to_peers (bool, optional): Whether the thread is anonymous to peers. Defaults to False.
            thread_type (str, optional): The type of the thread, either 'question' or 'discussion'.
            context (str, optional): The context of the thread, either 'course' or 'standalone'.

        Raises:
            ValueError: If `thread_type` is not 'question' or 'discussion'.
            ValueError: If `context` is not 'course' or 'standalone'.

        Returns:
            str: The ID of the inserted document.
        """
        if thread_type not in ["question", "discussion"]:
            raise ValueError("Invalid thread_type")

        if context not in ["course", "standalone"]:
            raise ValueError("Invalid context")

        date = datetime.now()
        thread_data = {
            "votes": self.get_votes(up=[], down=[]),
            "abuse_flaggers": [],
            "historical_abuse_flaggers": [],
            "thread_type": thread_type,
            "context": context,
            "comment_count": 0,
            "at_position_list": [],
            "title": title,
            "body": body,
            "course_id": course_id,
            "commentable_id": commentable_id,
            "_type": self.content_type,
            "anonymous": anonymous,
            "anonymous_to_peers": anonymous_to_peers,
            "closed": False,
            "author_id": author_id,
            "author_username": author_username,
            "created_at": date,
            "updated_at": date,
            "last_activity_at": date,
        }
        result = self.collection.insert_one(thread_data)
        return str(result.inserted_id)

    def update(
        self,
        thread_id: str,
        thread_type: Optional[str] = None,
        title: Optional[str] = None,
        body: Optional[str] = None,
        course_id: Optional[str] = None,
        anonymous: Optional[bool] = None,
        anonymous_to_peers: Optional[bool] = None,
        commentable_id: Optional[str] = None,
        at_position_list: Optional[List[str]] = None,
        closed: Optional[bool] = None,
        context: Optional[str] = None,
        author_id: Optional[str] = None,
        author_username: Optional[str] = None,
        votes: Optional[Dict[str, int]] = None,
        abuse_flaggers: Optional[List[str]] = None,
        closed_by: Optional[str] = None,
        pinned: Optional[bool] = None,
        comments_count: Optional[int] = None,
        endorsed: Optional[bool] = None,
    ):  # pylint: disable=arguments-differ
        """
        Updates a thread document in the database.

        Args:
            thread_id (str): The ID of the thread to update.
            thread_type (Optional[str], optional): The type of the thread, either 'question' or 'discussion'.
            title (Optional[str], optional): The title of the thread.
            body (Optional[str], optional): The body content of the thread.
            course_id (Optional[str], optional): The ID of the course the thread is associated with.
            anonymous (Optional[bool], optional): Whether the thread is posted anonymously.
            anonymous_to_peers (Optional[bool], optional): Whether the thread is anonymous to peers.
            commentable_id (Optional[str], optional): The ID of the commentable entity.
            at_position_list (Optional[List[str]], optional): A list of positions for @mentions.
            closed (Optional[bool], optional): Whether the thread is closed.
            context (Optional[str], optional): The context of the thread, either 'course' or 'standalone'.
            author_id (Optional[str], optional): The ID of the author who created the thread.
            author_username (Optional[str], optional): The username of the author.
            votes (Optional[Dict[str, int]], optional): The votes for the thread.
            abuse_flaggers (Optional[List[str]], optional): A list of users who flagged the thread for abuse.
            closed_by (Optional[str], optional): The ID of the user who closed the thread.
            pinned (Optional[bool], optional): Whether the thread is pinned.
            comments_count (Optional[int], optional): The number of comments on the thread.
            endorsed (Optional[bool], optional): Whether the thread is endorsed.

        Returns:
            int: The number of documents modified.
        """
        update_data = {}
        if thread_type:
            update_data["thread_type"] = thread_type
        if title:
            update_data["title"] = title
        if body:
            update_data["body"] = body
        if course_id:
            update_data["course_id"] = course_id
        if anonymous:
            update_data["anonymous"] = anonymous
        if anonymous_to_peers:
            update_data["anonymous_to_peers"] = anonymous_to_peers
        if commentable_id:
            update_data["commentable_id"] = commentable_id
        if at_position_list:
            update_data["at_position_list"] = at_position_list
        if closed:
            update_data["closed"] = closed
        if context:
            update_data["context"] = context
        if author_id:
            update_data["author_id"] = author_id
        if author_username:
            update_data["author_username"] = author_username
        if votes:
            update_data["votes"] = votes
        if abuse_flaggers:
            update_data["abuse_flaggers"] = abuse_flaggers
        if closed_by:
            update_data["closed_by"] = closed_by
        if pinned:
            update_data["pinned"] = pinned
        if comments_count:
            update_data["comments_count"] = comments_count
        if endorsed:
            update_data["endorsed"] = endorsed

        date = datetime.now()
        update_data["updated_at"] = date
        update_data["last_activity_at"] = date
        result = self.collection.update_one(
            {"_id": thread_id},
            {"$set": update_data},
        )
        return result.modified_count
