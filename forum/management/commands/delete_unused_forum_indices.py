"""Management command for deleting unused indices"""

from django.core.management.base import BaseCommand

from forum.search.es_helper import ElasticsearchHelper


class Command(BaseCommand):
    help = (
        "Delete all Elasticsearch indices that are not the latest for each model type."
    )

    def handle(self, *args: list[str], **kwargs: dict[str, str]) -> None:
        """
        Handles the execution of the delete_unused_forum_indices command.

        This command deletes all Elasticsearch indices that are not the latest for each model type.
        """
        es_helper = ElasticsearchHelper()
        indices_deleted_count = es_helper.delete_unused_indices()
        self.stdout.write(
            self.style.SUCCESS(
                f"{indices_deleted_count} unused indices deleted successfully."
            )
        )
