"""Content Class for mongo backend."""

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
