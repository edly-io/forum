"""Content Class for mongo backend."""

from datetime import datetime
from typing import Dict

from bson import ObjectId

from forum.models.base_model import MongoBaseModel


class Contents(MongoBaseModel):
    """
    Contents class for cs_comments_service contents collection
    """

    content_type = ""

    def __init__(self, collection_name="contents", client=None):
        """
        Initializes the Content class.
        Args:
            collection_name: The name of the MongoDB collection.
            client: The MongoDB client.
        """
        super().__init__(collection_name, client)

    def get(self, **kwargs):
        """
        Retrieves a contents documents from the database based on provided arguments.
        Args:
            kwargs: The filter arguments.
        Returns:
            The thread contents if found, otherwise None.
        """
        if self.content_type:
            kwargs["_type"] = self.content_type
        return self.collection.find_one(kwargs)

    def list(self, **kwargs):
        """
        Retrieves a list of all contents documents in the database based on provided filters.
        Args:
            kwargs: The filter arguments.
        Returns:
            A list of contents documents.
        """
        if self.content_type:
            kwargs["_type"] = self.content_type
        return self.collection.find(kwargs)

    def insert(self, **kwargs):
        """
        Return not implemented error on the insert
        """
        raise NotImplementedError

    def update(self, _id, **kwargs):
        """
        Return not implemented error on the insert
        """
        raise NotImplementedError

    @classmethod
    def get_votes_dict(cls, up=None, down=None):
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

    def update_votes(self, content_id: ObjectId, votes: Dict[str, int]):
        """
        Updates a votes in the content document.

        Args:
        content_id: The id of the content model
        votes (Optional[Dict[str, int]], optional): The votes for the thread.
        """
        update_data = {"votes": votes, "updated_at": datetime.now()}
        result = self.collection.update_one(
            {"_id": content_id},
            {"$set": update_data},
        )
        return result.modified_count
