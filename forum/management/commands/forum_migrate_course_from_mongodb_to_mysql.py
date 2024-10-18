"""Migration command for courses from mongodb to mysql."""

from typing import Any

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser

from forum.migration_helpers import (
    enable_mysql_backend_for_course,
    get_all_course_ids,
    migrate_content,
    migrate_read_states,
    migrate_users,
)
from forum.mongo import get_database


class Command(BaseCommand):
    """Migration command for courses from mongodb to mysql."""

    help = "Migrate data from MongoDB to MySQL"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments to the command."""
        parser.add_argument(
            "-T",
            "--no-toggle",
            action="store_true",
            help="Skip course waffle flag creation",
        )
        parser.add_argument(
            "courses", nargs="+", type=str, help="List of course IDs or `all`"
        )

    def handle(self, *args: str, **options: dict[str, Any]) -> None:
        """Handle the command."""
        db = get_database()

        create_waffle_flags = not options["no_toggle"]
        course_ids = list(options["courses"])
        if "all" in course_ids:
            course_ids = get_all_course_ids(db)

        for course_id in course_ids:
            self.stdout.write(f"Migrating data for course: {course_id}")
            migrate_users(db, course_id)
            migrate_content(db, course_id)
            migrate_read_states(db, course_id)
            if create_waffle_flags:
                enable_mysql_backend_for_course(course_id)
                self.stdout.write(
                    f"Enabled mysql backend waffle flag for course {course_id}."
                )

        self.stdout.write(self.style.SUCCESS("Data migration completed successfully"))
