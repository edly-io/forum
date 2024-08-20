"""Comment Class for mongo backend."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from forum.models.contents import BaseContents
from forum.models.users import Users


class Comment(BaseContents):
    """
    Comment class for cs_comments_service content model
    """

    content_type = "Comment"

    def insert(
        self,
        body: str,
        course_id: str,
        author_id: str,
        parent_id: Optional[str] = None,
        comment_thread_id: Optional[str] = None,
        author_username: Optional[str] = None,
        anonymous: bool = False,
        anonymous_to_peers: bool = False,
        depth: int = 0,
        abuse_flaggers: Optional[List[str]] = None,
        historical_abuse_flaggers: Optional[List[str]] = None,
        visible: bool = True,
    ) -> str:
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
            abuse_flaggers (Optional[List[str]], optional): Users who flagged the comment. Defaults to None.
            historical_abuse_flaggers (Optional[List[str]], optional): Users historically flagged the comment.
            visible (bool, optional): Whether the comment is visible. Defaults to True.

        Returns:
            str: The ID of the inserted document.
        """
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        parent_comment = parent_id and self.get(parent_id)
        parent_child_count = parent_comment and parent_comment.get("child_count")
        if parent_comment and not comment_thread_id:
            comment_thread_id = parent_comment.get("comment_thread_id")

        comment_data = {
            "votes": self.get_votes_dict(up=[], down=[]),
            "visible": visible,
            "abuse_flaggers": [] if abuse_flaggers is None else abuse_flaggers,
            "historical_abuse_flaggers": (
                [] if historical_abuse_flaggers is None else historical_abuse_flaggers
            ),
            "parent_ids": [ObjectId(parent_id)] if parent_id else [],
            "at_position_list": [],
            "body": body,
            "course_id": course_id,
            "_type": self.content_type,
            "endorsed": False,
            "anonymous": anonymous,
            "anonymous_to_peers": anonymous_to_peers,
            "parent_id": ObjectId(parent_id),
            "author_id": author_id,
            "comment_thread_id": ObjectId(comment_thread_id),
            "child_count": 0,
            "depth": depth,
            "author_username": author_username or self.get_author_username(author_id),
            "created_at": date,
            "updated_at": date,
        }
        result = self._collection.insert_one(comment_data)
        if parent_id and parent_child_count:
            self.update(parent_id, child_count=parent_child_count + 1)
        return str(result.inserted_id)

    def update(
        self,
        comment_id: str,
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
        historical_abuse_flaggers: Optional[List[str]] = None,
        endorsed: Optional[bool] = None,
        child_count: Optional[int] = None,
        depth: Optional[int] = None,
        closed: Optional[bool] = None,
        edit_history: Optional[list[dict[str, Any]]] = None,
        original_body: Optional[str] = None,
        editing_user_id: Optional[str] = None,
        edit_reason_code: Optional[str] = None,
        endorsement_user_id: Optional[str] = None,
    ) -> int:
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
            historical_abuse_flaggers (Optional[List[str]], optional): Users who historically flagged the comment.
            endorsed (Optional[bool], optional): Whether the comment is endorsed.
            child_count (Optional[int], optional): The number of child comments.
            depth (Optional[int], optional): The depth of the comment in the thread hierarchy.

        Returns:
            int: The number of documents modified.
        """
        fields = [
            ("body", body),
            ("course_id", course_id),
            ("anonymous", anonymous),
            ("anonymous_to_peers", anonymous_to_peers),
            ("comment_thread_id", comment_thread_id),
            ("at_position_list", at_position_list),
            ("visible", visible),
            ("author_id", author_id),
            ("author_username", author_username),
            ("votes", votes),
            ("abuse_flaggers", abuse_flaggers),
            ("historical_abuse_flaggers", historical_abuse_flaggers),
            ("endorsed", endorsed),
            ("child_count", child_count),
            ("depth", depth),
            ("closed", closed),
        ]
        update_data: Dict[str, Any] = {
            field: value for field, value in fields if value is not None
        }
        if endorsed and endorsement_user_id:
            update_data["endorsement"] = {
                "user_id": endorsement_user_id,
                "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

        if editing_user_id:
            edit_history = [] if edit_history is None else edit_history
            edit_history.append(
                {
                    "original_body": original_body,
                    "reason_code": edit_reason_code,
                    "editor_username": self.get_author_username(editing_user_id),
                    "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
            update_data["edit_history"] = edit_history

        update_data["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        result = self._collection.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": update_data},
        )
        return result.modified_count

    def delete(self, _id: str) -> int:
        """
        Deletes a comment from the database based on the id.

        Args:
            _id: The ID of the comment.

        Returns:
            The number of comments deleted.
        """
        comment = self.get(_id)
        parent_comment_id = comment and comment.get("parent_id")
        parent_comment = parent_comment_id and self.get(parent_comment_id)
        parent_comment_child_count = parent_comment and parent_comment.get(
            "child_count"
        )
        result = self._collection.delete_one({"_id": ObjectId(_id)})
        if parent_comment_id and parent_comment_child_count:
            self.update(parent_comment_id, child_count=parent_comment_child_count - 1)
        return result.deleted_count

    def get_author_username(self, author_id: str) -> str | None:
        """Return username for the respective author_id(user_id)"""
        user = Users().get(author_id)
        return user.get("username") if user else None
