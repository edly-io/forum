"""
Elasticsearch client utilities.
"""

from typing import Optional

from django.conf import settings
from elasticsearch import Elasticsearch

from forum.models import MODEL_INDICES, BaseContents

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
        return MODEL_INDICES

    @property
    def index_names(self) -> list[str]:
        """
        Retrieve the base index names for the configured models.

        Returns:
            list[str]: List of base index names.
        """
        return [model.index_name for model in self.models]
