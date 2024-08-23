"""Management command for initialize forum indices"""

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from forum.search.es_helper import ElasticsearchHelper


class Command(BaseCommand):
    help = "Initialize Elasticsearch indices, optionally forcing the creation of new indices."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """
        Adds command line arguments to the initialize_forum_indices command.

        Args:
            parser: The argument parser to which the --force argument is added.
        """
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force the creation of new indices even if they exist.",
        )

    def handle(self, *args: list[str], **kwargs: dict[str, Any]) -> None:
        """
        Handles the execution of the initialize_indices command.

        Initializes Elasticsearch indices. If the --force option is provided,
        it forces the creation of new indices even if they exist.

        Args:
            args: Additional arguments.
            kwargs: Command options.
        """
        es_helper = ElasticsearchHelper()
        force_new_index = bool(kwargs.get("force", False))
        es_helper.initialize_indices(force_new_index=force_new_index)
        self.stdout.write(self.style.SUCCESS("Forum indices initialized successfully."))
