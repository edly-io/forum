"""
Elasticsearch client utilities.
"""

from typing import Optional

from django.conf import settings
from elasticsearch import Elasticsearch

from forum.backends.mongodb import BaseContents
from forum.backends.mongodb import MODEL_INDICES as mongo_model_indices
from forum.backends.mysql import MODEL_INDICES as mysql_model_indices
from forum.models import Content

__all__ = ["Elasticsearch", "ElasticsearchModelMixin"]


class ElasticsearchModelMixin:
    """
    Provides convenient model and index name properties.
    """

    ELASTIC_SEARCH_INSTANCE: Optional[Elasticsearch] = None

    @property
    def client(self) -> Elasticsearch:
        """
        Elasticsearch client singleton.
        """
        if self.ELASTIC_SEARCH_INSTANCE is None:
            self.ELASTIC_SEARCH_INSTANCE = Elasticsearch(
                settings.FORUM_ELASTIC_SEARCH_CONFIG
            )
        return self.ELASTIC_SEARCH_INSTANCE

    @property
    def models(self) -> tuple[type[BaseContents], ...]:
        return mongo_model_indices

    @property
    def mysql_models(self) -> tuple[type[Content], ...]:
        return mysql_model_indices

    @property
    def index_names(self) -> list[str]:
        """
        Retrieve the base index names for the configured models.

        Returns:
            list[str]: List of base index names.
        """
        return [model.index_name for model in self.models]

    def get_mysql_model_from_index_name(self, index_name: str) -> type[Content]:
        for model in self.mysql_models:
            if index_name.startswith(model.index_name):
                return model
        raise Exception("Invalid model name")
