"""Content Class for mongo backend."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from forum.models.base_model import MongoBaseModel


class BaseContents(MongoBaseModel):
    """
    BaseContents class: same as Contents, but without "update" and "insert" methods,
    because child classes will have different signatures for these methods.
    """

    content_type: str = ""
    COLLECTION_NAME: str = "contents"

    def get(self, _id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a contents document from the database based on the provided _id.
        Args:
            _id: The ObjectId of the contents document to retrieve.
        Returns:
            The contents document if found, otherwise None.
        """
        return self._collection.find_one({"_id": ObjectId(_id)})

    def list(self, **kwargs: Any) -> Any:
        """
        Retrieves a list of all content documents in the database based on provided filters.

        Args:
            kwargs: The filter arguments.

        Returns:
            A list of content documents.
        """
        if self.content_type:
            kwargs["_type"] = self.content_type
        return self._collection.find(kwargs)

    @classmethod
    def get_votes_dict(cls, up: List[str], down: List[str]) -> Dict[str, Any]:
        """
        Calculates and returns the vote summary for a thread.

        Args:
            up (list): A list of user IDs who upvoted the thread.
            down (list): A list of user IDs who downvoted the thread.

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

    def update_votes(self, content_id: str, votes: Dict[str, Any]) -> int:
        """
        Updates a votes in the content document.

        Args:
        content_id: The id of the content model
        votes (Optional[Dict[str, int]], optional): The votes for the thread.
        """
        update_data = {"votes": votes, "updated_at": datetime.now()}
        result = self._collection.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": update_data},
        )
        return result.modified_count


class Contents(BaseContents):
    """
    Contents class for cs_comments_service contents collection
    """

    def insert(
        self,
        _id: str,
        author_id: str,
        abuse_flaggers: List[str],
        historical_abuse_flaggers: List[str],
        visible: bool,
    ) -> str:
        """
        Inserts a new content document into the database.

        Args:
            _id (str): The ID of the content.
            author_id (str): The ID of the author who created the content.
            abuse_flaggers (List[str]): A list of IDs of users who flagged the content as abusive.
            historical_abuse_flaggers (List[str]): A list of IDs of users who previously flagged the content as abusive.
            visible (bool): Whether the content is visible or not.

        Returns:
            str: The ID of the inserted document.
        """
        content_data = {
            "_id": ObjectId(_id),
            "author_id": author_id,
            "abuse_flaggers": abuse_flaggers,
            "historical_abuse_flaggers": historical_abuse_flaggers,
            "visible": visible,
        }
        result = self._collection.insert_one(content_data)
        return str(result.inserted_id)

    def update(self, _id: str, **kwargs: Any) -> int:
        """
        Updates a contents document in the database based on the provided _id.

        Args:
            _id: The id of the contents document to update.
            **kwargs: The fields to update in the contents document.

        Returns:
            The number of documents modified.
        """
        result = self._collection.update_one(
            {"_id": ObjectId(_id)},
            {"$set": {"abuse_flaggers": kwargs.get("abuse_flaggers")}},
        )
        return result.modified_count
