"""Test forum mongodb migration commands."""

from io import StringIO
from typing import Any

import pytest
from bson import ObjectId
from django.core.management import call_command
from django.contrib.auth.models import User  # pylint: disable=E5142
from django.utils import timezone
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

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def patch_enable_mysql_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch enable_mysql_backend_for_course to just return."""
    monkeypatch.setattr(
        "forum.migration_helpers.enable_mysql_backend_for_course",
        lambda course_id: None,
    )


def test_migrate_users(patched_mongodb: Database[Any]) -> None:
    patched_mongodb.users.insert_one(
        {
            "_id": "1",
            "username": "testuser",
            "default_sort_key": "date",
            "course_stats": [
                {
                    "course_id": "test_course",
                    "active_flags": 1,
                    "inactive_flags": 2,
                    "threads": 3,
                    "responses": 4,
                    "replies": 5,
                    "last_activity_at": timezone.now(),
                }
            ],
            "read_states": [
                {"course_id": "test_course", "last_read_times": {"1": timezone.now()}}
            ],
        }
    )

    call_command("forum_migrate_course_from_mongodb_to_mysql", "test_course")

    user = User.objects.get(pk=1)
    assert user.username == "testuser"
    forum_user = ForumUser.objects.get(user=user)
    assert forum_user.default_sort_key == "date"

    course_stat = CourseStat.objects.get(user=user, course_id="test_course")
    assert course_stat.active_flags == 1
    assert course_stat.inactive_flags == 2
    assert course_stat.threads == 3
    assert course_stat.responses == 4
    assert course_stat.replies == 5


def test_migrate_content(patched_mongodb: Database[Any]) -> None:
    patched_mongodb.users.insert_one(
        {
            "_id": "1",
            "username": "testuser",
            "default_sort_key": "date",
            "course_stats": [
                {
                    "course_id": "test_course",
                }
            ],
            "read_states": [
                {
                    "course_id": "test_course",
                    "last_read_times": {"000000000000000000000001": timezone.now()},
                }
            ],
        }
    )
    patched_mongodb.contents.insert_many(
        [
            {
                "_id": ObjectId("000000000000000000000001"),
                "_type": "CommentThread",
                "author_id": "1",
                "course_id": "test_course",
                "title": "Test Thread",
                "body": "Test body",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "votes": {"up": ["1"], "down": []},
            },
            {
                "_id": ObjectId("000000000000000000000002"),
                "_type": "Comment",
                "author_id": "1",
                "course_id": "test_course",
                "body": "Test comment",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "comment_thread_id": ObjectId("000000000000000000000001"),
                "votes": {"up": [], "down": ["1"]},
            },
        ]
    )

    user = User.objects.create(id=1, username="testuser")

    call_command("forum_migrate_course_from_mongodb_to_mysql", "test_course")

    thread = CommentThread.objects.get(
        pk=int(str(ObjectId("000000000000000000000001")), 16)
    )
    assert thread.title == "Test Thread"
    assert thread.body == "Test body"

    comment = Comment.objects.get(pk=int(str(ObjectId("000000000000000000000002")), 16))
    assert comment.body == "Test comment"
    assert comment.comment_thread == thread

    assert UserVote.objects.filter(content_object_id=thread.pk, vote=1).exists()
    assert UserVote.objects.filter(content_object_id=comment.pk, vote=-1).exists()

    read_state = ReadState.objects.get(user=user, course_id="test_course")
    assert LastReadTime.objects.filter(read_state=read_state).exists()


def test_migrate_subscriptions(patched_mongodb: Database[Any]) -> None:
    patched_mongodb.contents.insert_many(
        [
            {
                "_id": ObjectId("000000000000000000000001"),
                "_type": "CommentThread",
                "author_id": "1",
                "course_id": "test_course",
                "title": "Test Thread",
                "body": "Test body",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "votes": {"up": ["1"], "down": []},
            },
            {
                "_id": ObjectId("000000000000000000000002"),
                "_type": "Comment",
                "author_id": "1",
                "course_id": "test_course",
                "body": "Test comment",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "comment_thread_id": ObjectId("000000000000000000000001"),
                "votes": {"up": [], "down": ["1"]},
            },
        ]
    )
    patched_mongodb.subscriptions.insert_one(
        {
            "subscriber_id": "1",
            "source_id": ObjectId("000000000000000000000001"),
            "source_type": "CommentThread",
            "source": {"course_id": "test_course"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        }
    )

    user = User.objects.create(pk=1, username="testuser")
    thread = CommentThread.objects.create(
        pk=int(str(ObjectId("000000000000000000000001")), 16),
        author=user,
        course_id="test_course",
    )

    call_command("forum_migrate_course_from_mongodb_to_mysql", "test_course")

    assert Subscription.objects.filter(
        subscriber=user, source_object_id=thread.pk
    ).exists()


def test_delete_course_data(patched_mongodb: Database[Any]) -> None:
    patched_mongodb.users.insert_one(
        {
            "_id": "1",
            "username": "testuser",
            "default_sort_key": "date",
            "course_stats": [
                {
                    "course_id": "test_course",
                }
            ],
            "read_states": [
                {
                    "course_id": "test_course",
                    "last_read_times": {"000000000000000000000001": timezone.now()},
                }
            ],
        }
    )
    patched_mongodb.contents.insert_many(
        [
            {
                "_id": ObjectId("000000000000000000000001"),
                "_type": "CommentThread",
                "author_id": "1",
                "course_id": "test_course",
                "title": "Test Thread",
                "body": "Test body",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "votes": {"up": ["1"], "down": []},
            },
            {
                "_id": ObjectId("000000000000000000000002"),
                "_type": "Comment",
                "author_id": "1",
                "course_id": "test_course",
                "body": "Test comment",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "comment_thread_id": ObjectId("000000000000000000000001"),
                "votes": {"up": [], "down": ["1"]},
            },
        ]
    )
    patched_mongodb.subscriptions.insert_one(
        {
            "subscriber_id": "1",
            "source_id": ObjectId("000000000000000000000001"),
            "source_type": "CommentThread",
            "source": {"course_id": "test_course"},
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        }
    )

    out = StringIO()
    call_command("forum_delete_course_from_mongodb", "test_course", stdout=out)

    assert len(list(patched_mongodb.users.find())) == 1
    user = patched_mongodb.users.find_one()
    assert user
    assert user["course_stats"] == []
    assert user["read_states"] == []
    assert len(list(patched_mongodb.contents.find())) == 0
    assert len(list(patched_mongodb.subscriptions.find())) == 0

    output = out.getvalue()
    assert "Deleting data for course: test_course" in output
    assert "Cleaned up users collection" in output
    assert "Data deletion completed successfully" in output


def test_delete_dry_run(patched_mongodb: Database[Any]) -> None:
    """Call the command with dry-run option."""
    patched_mongodb.users.insert_one(
        {
            "_id": "1",
            "username": "testuser",
            "default_sort_key": "date",
            "course_stats": [
                {
                    "course_id": "test_course",
                }
            ],
            "read_states": [
                {
                    "course_id": "test_course",
                    "last_read_times": {"000000000000000000000001": timezone.now()},
                }
            ],
        }
    )
    patched_mongodb.contents.insert_one(
        {
            "_id": ObjectId("000000000000000000000001"),
            "_type": "CommentThread",
            "author_id": "1",
            "course_id": "test_course",
            "title": "Test Thread",
            "body": "Test body",
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "votes": {"up": ["1"], "down": []},
        }
    )
    out = StringIO()
    call_command(
        "forum_delete_course_from_mongodb", "test_course", "--dry-run", stdout=out
    )

    output = out.getvalue()
    assert "Performing dry run. No data will be deleted." in output
    assert "Dry run completed. No data was deleted." in output
    assert len(list(patched_mongodb.contents.find())) == 1


def test_delete_all_courses(patched_mongodb: Database[Any]) -> None:
    """Mock get_all_course_ids method."""
    patched_mongodb.users.insert_one(
        {
            "_id": "1",
            "username": "testuser",
            "default_sort_key": "date",
            "course_stats": [
                {
                    "course_id": "test_course_1",
                },
                {
                    "course_id": "test_course_2",
                },
            ],
            "read_states": [
                {
                    "course_id": "test_course_1",
                    "last_read_times": {"000000000000000000000001": timezone.now()},
                }
            ],
        }
    )
    patched_mongodb.contents.insert_many(
        [
            {
                "_id": ObjectId("000000000000000000000001"),
                "_type": "CommentThread",
                "author_id": "1",
                "course_id": "test_course_1",
                "title": "Test Thread",
                "body": "Test body",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "votes": {"up": ["1"], "down": []},
            },
            {
                "_id": ObjectId("000000000000000000000002"),
                "_type": "Comment",
                "author_id": "1",
                "course_id": "test_course_2",
                "body": "Test comment",
                "created_at": timezone.now(),
                "updated_at": timezone.now(),
                "comment_thread_id": ObjectId("000000000000000000000001"),
                "votes": {"up": [], "down": ["1"]},
            },
        ]
    )
    out = StringIO()
    call_command("forum_delete_course_from_mongodb", "all", stdout=out)

    output = out.getvalue()
    assert len(list(patched_mongodb.contents.find())) == 0
    assert "Deleting data for course: test_course_1" in output
    assert "Deleting data for course: test_course_2" in output
