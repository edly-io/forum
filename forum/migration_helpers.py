"""Migration commands helper methods."""

from typing import Any

from django.contrib.auth.models import User  # pylint: disable=E5142
from django.core.management.base import OutputWrapper
from django.utils import timezone
from pymongo.collection import Collection
from pymongo.database import Database

from forum.models import (
    ForumUser,
    CourseStat,
    ReadState,
    LastReadTime,
    CommentThread,
    Comment,
    UserVote,
    Subscription,
)


def get_all_course_ids(db: Database[dict[str, Any]]) -> list[str]:
    """Get all course IDs from MongoDB."""
    return db.contents.distinct("course_id")


def migrate_users(db: Database[dict[str, Any]], course_id: str) -> None:
    """Migrate users from MongoDB to MySQL."""
    users = db.users.find({"course_stats.course_id": course_id})
    for user_data in users:
        user, _ = User.objects.get_or_create(
            id=int(user_data["_id"]), defaults={"username": user_data["username"]}
        )

        _, _ = ForumUser.objects.get_or_create(
            user=user,
            defaults={"default_sort_key": user_data.get("default_sort_key", "date")},
        )

        for stat in user_data.get("course_stats", []):
            if stat["course_id"] == course_id:
                CourseStat.objects.update_or_create(
                    user=user,
                    course_id=course_id,
                    defaults={
                        "active_flags": stat.get("active_flags", 0),
                        "inactive_flags": stat.get("inactive_flags", 0),
                        "threads": stat.get("threads", 0),
                        "responses": stat.get("responses", 0),
                        "replies": stat.get("replies", 0),
                        "last_activity_at": stat.get("last_activity_at"),
                    },
                )


def migrate_content(db: Database[dict[str, Any]], course_id: str) -> None:
    """Migrate content from MongoDB to MySQL."""
    contents = db.contents.find({"course_id": course_id})
    for content in contents:
        if content["_type"] == "CommentThread":
            create_or_update_thread(content)
        elif content["_type"] == "Comment":
            create_or_update_comment(content)

        migrate_subscriptions(db, content["_id"])


def create_or_update_thread(thread_data: dict[str, Any]) -> None:
    """Create or update a thread."""
    author = User.objects.get(id=int(thread_data["author_id"]))
    thread, _ = CommentThread.objects.update_or_create(
        id=int(str(thread_data["_id"]), 16),
        defaults={
            "author": author,
            "course_id": thread_data["course_id"],
            "title": thread_data.get("title", ""),
            "body": thread_data["body"],
            "thread_type": thread_data.get("thread_type", "discussion"),
            "context": thread_data.get("context", "course"),
            "anonymous": thread_data.get("anonymous", False),
            "anonymous_to_peers": thread_data.get("anonymous_to_peers", False),
            "closed": thread_data.get("closed", False),
            "pinned": thread_data.get("pinned"),
            "created_at": thread_data["created_at"],
            "updated_at": thread_data["updated_at"],
        },
    )
    create_votes(thread, thread_data.get("votes", {}))


def create_or_update_comment(comment_data: dict[str, Any]) -> None:
    """Create or update a comment."""
    author = User.objects.get(id=int(comment_data["author_id"]))
    thread = CommentThread.objects.get(
        id=int(str(comment_data["comment_thread_id"]), 16)
    )
    parent = None
    if "parent_id" in comment_data and comment_data["parent_id"] != "None":
        parent = Comment.objects.filter(
            id=int(str(comment_data["parent_id"]), 16)
        ).first()

    comment, _ = Comment.objects.update_or_create(
        id=int(str(comment_data["_id"]), 16),
        defaults={
            "author": author,
            "comment_thread": thread,
            "parent": parent,
            "course_id": comment_data["course_id"],
            "body": comment_data["body"],
            "anonymous": comment_data.get("anonymous", False),
            "anonymous_to_peers": comment_data.get("anonymous_to_peers", False),
            "endorsed": comment_data.get("endorsed", False),
            "child_count": comment_data.get("child_count", 0),
            "created_at": comment_data["created_at"],
            "updated_at": comment_data["updated_at"],
        },
    )
    create_votes(comment, comment_data.get("votes", {}))


def create_votes(content: CommentThread | Comment, votes_data: dict[str, Any]) -> None:
    """Create or update votes for a content."""
    for vote_type in ["up", "down"]:
        for user_id in votes_data.get(vote_type, []):
            user = User.objects.get(pk=int(user_id))
            UserVote.objects.update_or_create(
                user=user,
                content_type=content.content_type,
                content_object_id=content.pk,
                defaults={"vote": 1 if vote_type == "up" else -1},
            )


def migrate_subscriptions(db: Database[dict[str, Any]], content_id: str) -> None:
    """Migrate subscriptions from mongo to mysql."""
    subscriptions = db.subscriptions.find({"source_id": content_id})
    for sub in subscriptions:
        user = User.objects.get(id=int(sub["subscriber_id"]))
        content_type = (
            CommentThread if sub["source_type"] == "CommentThread" else Comment
        )
        content = content_type.objects.filter(id=int(str(content_id), 16)).first()

        if content:
            Subscription.objects.update_or_create(
                subscriber=user,
                source_content_type=content.content_type,
                source_object_id=content.pk,
                defaults={
                    "created_at": sub.get("created_at", timezone.now()),
                    "updated_at": sub.get("updated_at", timezone.now()),
                },
            )


def migrate_read_states(db: Database[dict[str, Any]], course_id: str) -> None:
    """Migrate read states from mongo to mysql."""
    users = db.users.find({"course_stats.course_id": course_id})
    for user_data in users:
        try:
            user = User.objects.get(id=int(user_data["_id"]))
        except User.DoesNotExist:
            continue

        for read_state in user_data.get("read_states", []):
            if read_state["course_id"] == course_id:
                rs, _ = ReadState.objects.get_or_create(user=user, course_id=course_id)
                for thread_id, timestamp in read_state.get(
                    "last_read_times", {}
                ).items():
                    thread = CommentThread.objects.filter(id=thread_id).first()
                    if thread:
                        LastReadTime.objects.update_or_create(
                            read_state=rs,
                            comment_thread=thread,
                            defaults={"timestamp": timestamp},
                        )


def delete_course_data(
    db: Database[dict[str, Any]],
    course_id: str,
    dry_run: bool,
    stdout: OutputWrapper,
) -> None:
    """Delete content (threads and comments)."""
    contents = db.contents.find({"course_id": course_id})
    for content in contents:
        subscriptions = (
            db.subscriptions.delete_many({"source_id": content["_id"]})
            if not dry_run
            else None
        )
    stdout.write(
        f"Subscription documents to be deleted: {subscriptions.deleted_count if subscriptions else 'N/A (dry run)'}"
    )

    content_result = (
        db.contents.delete_many({"course_id": course_id}) if not dry_run else None
    )
    stdout.write(
        f"Content documents to be deleted: {content_result.deleted_count if content_result else 'N/A (dry run)'}"
    )
    user_ids = db.users.distinct("_id", {"course_stats.course_id": course_id})

    for user_id in user_ids:
        if not dry_run:
            db.users.update_one(
                {"_id": user_id},
                {
                    "$pull": {
                        "course_stats": {"course_id": course_id},
                        "read_states": {"course_id": course_id},
                    }
                },
            )
        stdout.write(f"Updated user data for user ID: {user_id}")

    if not dry_run:
        db.users.update_many(
            {},
            {
                "$pull": {
                    "course_stats": {"course_id": course_id},
                    "read_states": {"course_id": course_id},
                }
            },
        )
    stdout.write("Cleaned up users collection")


def log_deletion(
    collection_name: str,
    result: Collection[dict[str, Any]],
    stdout: OutputWrapper,
) -> None:
    """Log the deletion of a collection."""
    stdout.write(f"Deleted {result.deleted_count} documents from {collection_name}")


def enable_mysql_backend_for_course(course_id: str) -> None:
    """Enable MySQL backend waffle flag for a course."""
    # pylint: disable=C0415,E0401
    from opaque_keys.edx.locator import CourseKey  # type: ignore[import-not-found]
    from openedx.core.djangoapps.waffle_utils import WaffleFlagCourseOverrideModel  # type: ignore[import-not-found]
    from forum.toggles import ENABLE_MYSQL_BACKEND

    course_key = CourseKey.from_string(course_id)
    mysql_waffle_flag, _ = WaffleFlagCourseOverrideModel.objects.get_or_create(
        course_id=course_key, waffle_flag=ENABLE_MYSQL_BACKEND.name
    )
    mysql_waffle_flag.enabled = True
    mysql_waffle_flag.save()
