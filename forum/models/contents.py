"""Content Class for mongo backend."""

from typing import Any, Dict, List, Optional

from bson import ObjectId

from forum.models.base_model import MongoBaseModel
from forum.mongo import MongoBackend


class Contents(MongoBaseModel):
    """
    Contents class for cs_comments_service contents collection
    """

    content_type: str = ""

    def __init__(
        self, collection_name: str = "contents", client: Optional[MongoBackend] = None
    ) -> None:
        """
        Initializes the Content class.

        Args:
            collection_name: The name of the MongoDB collection.
            client: The MongoDB client.
        """
        super().__init__(collection_name, client)

    def get(self, _id: str) -> Optional[Dict[str, Any]]:  # pylint: disable=arguments-differ
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

    def insert(  # pylint: disable=arguments-differ
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

    def update(self, _id: str, **kwargs: Any) -> int:  # pylint: disable=arguments-differ
        """
        Updates a contents document in the database based on the provided _id.

        Args:
            _id: The id of the contents document to update.
            **kwargs: The fields to update in the contents document.

        Returns:
            The number of documents modified.
        """
        update_data = {}

        update_data["abuse_flaggers"] = kwargs.get("abuse_flaggers")

        result = self._collection.update_one(
            {"_id": ObjectId(_id)},
            {"$set": update_data},
        )
        return result.modified_count
