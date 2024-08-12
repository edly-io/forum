# pylint: disable=arguments-differ

"""Users Class for mongo backend."""

from typing import Any, Dict, List, Optional

from forum.models.base_model import MongoBaseModel
from forum.mongo import MongoBackend


class Users(MongoBaseModel):
    """
    Users class for cs_comments_service user model
    """

    def __init__(
        self, collection_name: str = "users", client: Optional[MongoBackend] = None
    ) -> None:
        """
        Initializes the Users class.

        Args:
            collection_name: The name of the MongoDB collection.
            client: The MongoDB client.

        """
        super().__init__(collection_name, client)

    def insert(
        self,
        external_id: str,
        username: str,
        email: str,
        default_sort_key: str = "date",
        read_states: Optional[List[Dict[str, Any]]] = None,
        course_stats: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Inserts a new user document into the database.

        Args:
            external_id: The external ID of the user.
            username: The username of the user.
            email: The email of the user.
            default_sort_key: The default sort key for the user.
            read_states: The read states of the user.
            course_stats: The course statistics of the user.

        Returns:
            The ID of the inserted document.

        """
        user_data: Dict[str, Any] = {
            "_id": external_id,
            "external_id": external_id,
            "username": username,
            "email": email,
            "default_sort_key": default_sort_key,
            "read_states": read_states,
            "course_stats": course_stats,
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def delete(self, _id: Any) -> int:
        """
        Deletes a user document from the database based on the id.

        Args:
            _id: The ID of the user.

        Returns:
            The number of documents deleted.

        """
        result = self.collection.delete_one({"_id": _id})
        return result.deleted_count

    def update(
        self,
        external_id: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        default_sort_key: Optional[str] = None,
        read_states: Optional[List[Dict[str, Any]]] = None,
        course_stats: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Updates a user document in the database based on the external_id.

        Args:
            external_id: The external ID of the user.
            username: The new username of the user.
            email: The new email of the user.
            default_sort_key: The new default sort key for the user.
            read_states: The new read states of the user.
            course_stats: The new course statistics of the user.

        Returns:
            The number of documents modified.

        """
        fields = [
            ("username", username),
            ("email", email),
            ("default_sort_key", default_sort_key),
            ("read_states", read_states),
            ("course_stats", course_stats),
        ]
        update_data: dict[str, Any] = {
            field: value for field, value in fields if value is not None
        }

        result = self.collection.update_one(
            {"external_id": external_id},
            {"$set": update_data},
        )
        return result.modified_count
