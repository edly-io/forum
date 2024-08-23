"""
Helper for managing elastic search queries.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Iterator, Optional, Union

from django.conf import settings
from elasticsearch import Elasticsearch, exceptions, helpers

from forum.models import Comment, CommentThread
from forum.models.contents import BaseContents

log = logging.getLogger(__name__)


class ElasticsearchHelper:
    """
    Helper class for managing Forum indices.
    """

    temporary_index_names: list[str] = []

    def __init__(self) -> None:
        """
        Initialize the Elasticsearch client and sets up the models to be indexed.
        """
        self.client: Elasticsearch = Elasticsearch(settings.ELASTIC_SEARCH_CONFIG)
        self.models = [CommentThread, Comment]

    def index_names(self) -> list[str]:
        """
        Retrieve the index names for the configured models.

        Returns:
            list[str]: List of index names.
        """
        return [model.index_name for model in self.models]

    def add_temporary_index_names(self, index_names: list[str]) -> None:
        """
        Add the provided index names to the temporary index list.

        Args:
            index_names (list[str]): List of index names to add.
        """
        self.temporary_index_names = index_names

    def rebuild_indices(
        self, batch_size: int = 500, extra_catchup_minutes: int = 5
    ) -> None:
        """
        Rebuild the indices by creating new indices, importing data, and managing aliases.

        Args:
            batch_size (int): Number of documents to process in each batch.
            extra_catchup_minutes (int): Extra minutes to adjust the start time for catch-up.
        """
        initial_start_time = datetime.now()

        index_names = self.create_indices()
        for index_name in index_names:
            current_batch = 1
            model = self.get_index_model_rel(index_name)
            for response in self._import_to_es(model, index_name, batch_size):
                self.batch_import_post_process(response, current_batch)
                current_batch += 1

        first_catchup_start_time = datetime.now()
        adjusted_start_time = initial_start_time - timedelta(
            minutes=extra_catchup_minutes
        )
        self.catchup_indices(index_names, adjusted_start_time, batch_size)

        alias_names = []
        for index_name in index_names:
            current_batch = 1
            model = self.get_index_model_rel(index_name)
            alias_names.append(model.index_name)
            self.move_alias(model.index_name, index_name, force_delete=True)

        adjusted_start_time = first_catchup_start_time - timedelta(
            minutes=extra_catchup_minutes
        )
        self.catchup_indices(alias_names, adjusted_start_time, batch_size)

        self.add_temporary_index_names(index_names)
        log.info("Rebuild indices complete.")

    def get_index_model_rel(self, index_name: str) -> BaseContents:
        """
        Retrieve the model corresponding to the given index name.

        Args:
            index_name (str): Name of the index.

        Returns:
            model: The model associated with the index name.
        """
        for model in self.models:
            if index_name.startswith(model.index_name):
                return model()
        raise ValueError("Invalid index name")

    def catchup_indices(
        self, index_names: list[str], start_time: datetime, batch_size: int = 100
    ) -> None:
        """
        Catche up the indices by importing documents updated after the specified start time.

        Args:
            index_names (list[str]): List of index names to catch up.
            start_time (datetime): The starting time for catching up.
            batch_size (int): Number of documents to process in each batch.
        """
        for index_name in index_names:
            current_batch = 1
            model = self.get_index_model_rel(index_name)
            query = {"updated_at": {"$gte": start_time}}
            for response in self._import_to_es(model, index_name, batch_size, query):
                self.batch_import_post_process(response, current_batch)
                current_batch += 1
        log.info(f"Catch up from {start_time} complete.")

    def create_indices(self) -> list[str]:
        """
        Create new indices for each model with the current timestamp in the index name.

        Returns:
            list[str]: List of newly created index names.
        """
        index_names = []
        time_now = datetime.now().strftime("%Y%m%d%H%M%S%f")

        for model in self.models:
            index_name = f"{model.index_name}_{time_now}"
            index_names.append(index_name)
            self.client.indices.create(
                index=index_name, body={"mappings": model.mapping()}
            )
        log.info(f"New indices {index_names} are created.")
        return index_names

    def delete_index(self, name: str) -> None:
        """
        Delete the specified index.

        Args:
            name (str): The name of the index to delete.
        """
        self.client.indices.delete(index=name)
        log.info(f"Deleted index: {name}.")

    def delete_indices(self) -> None:
        """
        Delete all temporary indices.
        """
        if self.temporary_index_names:
            try:
                self.client.indices.delete(index=self.temporary_index_names)
                log.info(f"Indices {self.temporary_index_names} are deleted.")
            except exceptions.NotFoundError as error:
                log.error(
                    f"Enable to delete indices {self.temporary_index_names}: {error}"
                )
        else:
            log.info("No Indices to delete.")

    def batch_import_post_process(
        self, response: tuple[int, Any], batch_number: int
    ) -> None:
        """
        Process the response from a batch import operation.

        Args:
            response (tuple[int, list[dict]]): Tuple containing the count of successful imports and a list of errors.
            batch_number (int): The current batch number being processed.
        """
        success_count, errors = response
        for item in errors:
            if "error" in item["index"]:
                log.error(f"Error indexing. Response was: {response}")
        log.info(
            f"Imported {success_count} documents to the batch {batch_number} into the index"
        )

    def get_index_shard_count(self, name: str) -> int:
        """
        Retrieve the shard count for the specified index.

        Args:
            name (str): The name of the index.

        Returns:
            int: Number of shards for the index.
        """
        es_settings = self.client.indices.get_settings(index=name)
        return int(es_settings[name]["settings"]["index"]["number_of_shards"])

    def exists_alias(self, alias_name: str) -> bool:
        """
        Check if an alias exists.

        Args:
            alias_name (str): The alias name to check.

        Returns:
            bool: True if the alias exists, False otherwise.
        """
        return self.client.indices.exists_alias(name=alias_name)

    def exists_indices(self) -> bool:
        """
        Check if any of the temporary indices exist.

        Returns:
            bool: True if any temporary index exists, False otherwise.
        """
        return self.client.indices.exists(index=self.temporary_index_names)

    def exists_aliases(self, aliases: list[str]) -> bool:
        """
        Check if the specified aliases exist.

        Args:
            aliases (list[str]): List of alias names to check.

        Returns:
            bool: True if all aliases exist, False otherwise.
        """
        return self.client.indices.exists_alias(name=aliases)

    def exists_index(self, index_name: str) -> bool:
        """
        Check if a specific index exists.

        Args:
            index_name (str): The name of the index to check.

        Returns:
            bool: True if the index exists, False otherwise.
        """
        return self.client.indices.exists(index=index_name)

    def move_alias(
        self, alias_name: str, index_name: str, force_delete: bool = False
    ) -> None:
        """
        Move an alias to point to a new index, optionally deleting an existing index with the same name.

        Args:
            alias_name (str): The alias name to move.
            index_name (str): The new index name to point the alias to.
            force_delete (bool): If True, deletes any existing index with the alias name before moving the alias.

        Raises:
            ValueError: If the alias name matches the index name or if the index doesn't exist.
        """
        if alias_name == index_name:
            raise ValueError(
                f"Can't point alias [{alias_name}] to an index of the same name."
            )
        if not self.exists_index(index_name):
            raise ValueError(f"Can't point alias to non-existent index [{index_name}].")

        if self.exists_index(alias_name) and not self.exists_alias(alias_name):
            if force_delete:
                self.delete_index(alias_name)
            else:
                raise ValueError(
                    f"Can't create alias [{alias_name}] because there is already an "
                    f"auto-generated index of the same name. Try again with force_delete=True to first "
                    f"delete this pre-existing index."
                )

        actions = [{"add": {"index": index_name, "alias": alias_name}}]

        try:
            response = self.client.indices.get_alias(name=alias_name)
            if response:
                actions.insert(
                    0,
                    {
                        "remove": {
                            "index": ",".join(response.keys()),
                            "alias": alias_name,
                        }
                    },
                )
        except exceptions.NotFoundError as e:
            log.warning(f"Alias not found for {alias_name}: {e}")

        self.client.indices.update_aliases(body={"actions": actions})
        log.info(f"Alias [{alias_name}] now points to index [{index_name}].")

    def refresh_indices(self) -> None:
        """
        Refresh the indices associated with the temporary index names.

        Raises:
            ValueError: If no indices are available to refresh.
        """
        if self.temporary_index_names:
            self.client.indices.refresh(index=self.index_names())
        else:
            raise ValueError("No indices to refresh")

    def initialize_indices(self, force_new_index: bool = False) -> None:
        """
        Initialize the indices by creating new indices or reusing existing ones based on aliases.

        Args:
            force_new_index (bool): If True, forces the creation of new indices regardless of existing ones.
        """
        if force_new_index or not self.exists_aliases(self.index_names()):
            index_names = self.create_indices()
            for index_name in index_names:
                model = self.get_index_model_rel(index_name)
                self.move_alias(model.index_name, index_name, force_delete=True)
            self.add_temporary_index_names(index_names)
        else:
            log.info("Skipping initialization. Indices already exist.")

    def validate_indices(self) -> None:
        """
        Validate that the indices have the correct mappings and properties.

        Raises:
            ValueError: If indices do not exist, or mappings/properties are missing or incorrect.
        """
        actual_mappings = self.client.indices.get_mapping(index=self.index_names())

        if not actual_mappings:
            raise ValueError("Indices do not exist!")

        for index_name in actual_mappings:
            model = self.get_index_model_rel(index_name)
            expected_mapping = model.mapping()
            actual_mapping = actual_mappings[index_name]["mappings"]

            if set(actual_mapping.keys()) != set(expected_mapping.keys()):
                raise ValueError(
                    f"Actual mapping [{list(actual_mapping.keys())}] "
                    f"does not match expected mapping [{list(expected_mapping.keys())}]."
                )

            actual_props = actual_mapping["properties"]
            expected_props = expected_mapping["properties"]
            missing_fields = [
                prop for prop in expected_props if prop not in actual_props
            ]
            invalid_types = [
                f"'{prop}' type '{actual_type['type']}' should be '{expected_type['type']}'"
                for prop, expected_type in expected_props.items()
                if (actual_type := actual_props.get(prop))
                and actual_type["type"] != expected_type["type"]
            ]

            if missing_fields or invalid_types:
                raise ValueError(
                    f"Index '{model.index_name}' has missing or invalid field mappings.  "
                    f"Missing fields: {missing_fields}. Invalid types: {invalid_types}."
                )

            log.info(
                f"Passed: Index '{model.index_name}' exists with up-to-date mappings."
            )

    def _import_to_es(
        self,
        model: BaseContents,
        index_name: str,
        batch_size: int,
        query: Optional[dict[str, Any]] = None,
    ) -> Iterator[tuple[int, Union[int, list[Any]]]]:
        """
        Import data from the given model into Elasticsearch in batches.

        Args:
            model: The model to import data from.
            index_name (str): The name of the Elasticsearch index.
            batch_size (int): Number of documents to process in each batch.
            query (dict, optional): MongoDB query to filter documents. Defaults to None.

        Yields:
            tuple[int, list[dict]]: Tuple containing the count of successful imports and a list of errors.
        """
        cursor = model.find(query or {}).batch_size(batch_size)
        actions = []
        for doc in cursor:
            action = {
                "_index": index_name,
                "_id": str(doc.get("_id")),
                "_source": model.doc_to_hash(doc),
            }
            actions.append(action)
            if len(actions) >= batch_size:
                yield helpers.bulk(self.client, actions)
                actions = []
        if actions:
            yield helpers.bulk(self.client, actions)

    def delete_unused_indices(self) -> int:
        """
        Delete all Elasticsearch indices that are not the latest for each model type.

        This method fetches all indices matching the patterns from the models, determines the latest index
        for each model type, and deletes all other indices.

        Raises:
            Exception: If there's an error during the deletion process.
        """
        # Get index patterns from model index names
        index_patterns = [f"{pattern}*" for pattern in self.index_names()]

        # Get all indices that match the patterns
        all_indices = []
        for pattern in index_patterns:
            indices = self.client.indices.get(pattern)
            all_indices.extend(indices.keys())

        # Determine the latest index for each model type
        latest_indices: dict[str, Any] = {}
        for index_name in all_indices:
            for base_name in self.index_names():
                if index_name.startswith(base_name):
                    match = re.search(r"\d{14}", index_name)
                    if match:
                        index_timestamp_str = match.group()
                        index_timestamp = datetime.strptime(
                            index_timestamp_str, "%Y%m%d%H%M%S"
                        )

                        if (
                            base_name not in latest_indices
                            or index_timestamp > latest_indices[base_name][1]
                        ):
                            latest_indices[base_name] = (
                                index_name,
                                index_timestamp,
                            )

        # List of all indices to delete (all indices except the latest ones)
        indices_to_keep = {info[0] for info in latest_indices.values()}
        indices_to_delete = set(all_indices) - indices_to_keep

        if not indices_to_delete:
            log.info("No old indices to delete.")
            return 0

        # Delete old indices
        self.client.indices.delete(index=",".join(indices_to_delete))
        log.info(f"Deleted unused indices: {indices_to_delete}")

        return len(indices_to_delete)
