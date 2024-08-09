"""Content Class for mongo backend."""

from typing import Optional, Dict, Any
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

    def get(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieves a content document from the database based on provided arguments.

        Args:
            kwargs: The filter arguments.

        Returns:
            The thread contents if found, otherwise None.
        """
        if self.content_type:
            kwargs["_type"] = self.content_type
        return self.collection.find_one(kwargs)

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
        return self.collection.find(kwargs)

    def insert(self, **kwargs: Any) -> str:
        """
        Return not implemented error on the insert.
        """
        raise NotImplementedError
