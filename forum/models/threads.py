"""Content Class for mongo backend."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from forum.models.contents import Contents


class CommentThread(Contents):
    """
    CommentThread class for cs_comments_service content model
    """

    content_type = "CommentThread"

    def get_votes(
        self, up: Optional[List[str]] = None, down: Optional[List[str]] = None
    ) -> Dict[str, object]:
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

    def insert(self, **kwargs: Any) -> str:
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
        thread_type = kwargs.get("thread_type", "discussion")
        if thread_type not in ["question", "discussion"]:
            raise ValueError("Invalid thread_type")

        context = kwargs.get("context", "course")
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
            "title": kwargs.get("title", ""),
            "body": kwargs.get("body", ""),
            "course_id": kwargs.get("course_id", ""),
            "commentable_id": kwargs.get("commentable_id", ""),
            "_type": self.content_type,
            "anonymous": kwargs.get("anonymous", False),
            "anonymous_to_peers": kwargs.get("anonymous_to_peers", False),
            "closed": False,
            "author_id": kwargs.get("author_id", ""),
            "author_username": kwargs.get("author_username", ""),
            "created_at": date,
            "updated_at": date,
            "last_activity_at": date,
        }
        result = self.collection.insert_one(thread_data)
        return str(result.inserted_id)

    def update(self, **kwargs: Any) -> int:
        """
        Updates a thread document in the database.

        Args:
            thread_id (str): The ID of the thread to update.
            ...
            endorsed (Optional[bool], optional): Whether the thread is endorsed.

        Returns:
            int: The number of documents modified.
        """
        fields = [
            "thread_type",
            "title",
            "body",
            "course_id",
            "anonymous",
            "anonymous_to_peers",
            "commentable_id",
            "at_position_list",
            "closed",
            "context",
            "author_id",
            "author_username",
            "votes",
            "abuse_flaggers",
            "closed_by",
            "pinned",
            "comments_count",
            "endorsed",
        ]
        update_data = {field: kwargs[field] for field in fields if field in kwargs}

        date = datetime.now()
        update_data["updated_at"] = date
        update_data["last_activity_at"] = date
        result = self.collection.update_one(
            {"_id": kwargs.get("thread_id", "")},
            {"$set": update_data},
        )
        return result.modified_count
