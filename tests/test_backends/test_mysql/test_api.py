"""Tests for db client."""

import pytest
from django.contrib.auth import get_user_model

from forum.backends.mysql.models import (
    AbuseFlagger,
    CommentThread,
)
from forum.backends.mysql.api import MySQLBackend as backend

User = get_user_model()


@pytest.mark.django_db
def test_flag_as_abuse() -> None:
    """Test flagging a comment as abuse."""
    author = User.objects.create(username="author-user")
    flag_user = User.objects.create(username="flag-user")
    comment_thread = CommentThread.objects.create(
        author=author,
        course_id="course123",
        title="Test Thread",
        body="This is a test thread",
        thread_type="discussion",
        context="course",
    )
    flagged_comment_thread = backend.flag_as_abuse(
        str(flag_user.pk),
        str(comment_thread.pk),
        entity_type=comment_thread.type,
    )

    assert flagged_comment_thread["_id"] == str(comment_thread.pk)
    assert flagged_comment_thread["abuse_flaggers"] == [str(flag_user.pk)]


@pytest.mark.django_db
def test_un_flag_as_abuse_success() -> None:
    """test for un_flag_as_abuse works successfully."""
    user = User.objects.create(username="testuser")
    comment_thread = CommentThread.objects.create(
        author=user,
        course_id="course123",
        title="Test Thread",
        body="This is a test thread",
        thread_type="discussion",
        context="course",
    )
    AbuseFlagger.objects.create(user=user, content=comment_thread)
    comment_thread.save()
    un_flagged_entity = backend.un_flag_as_abuse(
        user.pk,
        comment_thread.pk,
        entity_type=comment_thread.type,
    )

    assert user.pk not in comment_thread.abuse_flaggers
    assert un_flagged_entity["_id"] == str(comment_thread.pk)
    assert (
        AbuseFlagger.objects.filter(
            user=user, content_object_id=comment_thread.pk
        ).count()
        == 0
    )


@pytest.mark.django_db
def test_un_flag_all_as_abuse_historical_flags_updated() -> None:
    """test for un_flag_as_abuse updates historical flags."""
    user = User.objects.create(username="testuser")
    comment_thread = CommentThread.objects.create(
        author=user,
        course_id="course123",
        title="Test Thread",
        body="This is a test thread",
        thread_type="discussion",
        context="course",
    )
    AbuseFlagger.objects.create(user=user, content=comment_thread)
    un_flagged_comment_thread = backend.un_flag_all_as_abuse(
        comment_thread.pk,
        entity_type=comment_thread.type,
    )

    assert un_flagged_comment_thread["_id"] == str(comment_thread.pk)
    assert len(comment_thread.abuse_flaggers) == 0
    assert len(comment_thread.historical_abuse_flaggers) == 1
