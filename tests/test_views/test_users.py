"""Tests for Users apis."""

import random
from typing import Any

import pytest

from forum.constants import RETIRED_BODY, RETIRED_TITLE
from forum.models import Comment, CommentThread, Contents, Users
from forum.models.model_utils import subscribe_user, upvote_content
from test_utils.client import APIClient


def setup_10_threads() -> None:
    """Create 10 threads for a user."""
    for thread in range(10):
        thread_id = CommentThread().insert(
            title=f"Test Thread {thread}",
            body="This is a test thread",
            course_id="course1",
            commentable_id="commentable1",
            author_id="test_id",
            author_username="test-user",
        )
        Comment().insert(
            body="This is a test comment",
            course_id="course1",
            author_id="test_id",
            comment_thread_id=str(thread_id),
            author_username="test-user",
        )


@pytest.fixture(name="build_structure_and_response")
def fixture_build_structure_and_response() -> dict[str, Any]:
    """Fixture for creating course stats."""
    course_id = "test_course"
    authors = ["author-1", "author-2", "author-3", "author-4", "author-5", "author-6"]
    for author in authors:
        Users().insert(author, author)

    expected_data: dict[str, dict[str, Any]] = {
        author: {
            "username": author,
            "active_flags": 0,
            "inactive_flags": 0,
            "threads": 0,
            "responses": 0,
            "replies": 0,
        }
        for author in authors
    }
    for _ in range(10):
        thread_author = random.choice(authors)
        expected_data[thread_author]["threads"] += 1
        thread_id = CommentThread().insert(
            title="Test Thread",
            body="This is a test thread",
            course_id=course_id,
            commentable_id="commentable1",
            author_id=thread_author,
            author_username=thread_author,
        )
        abuse_flaggers = random.sample(range(1, 3), random.randint(0, 2))
        historical_abuse_flaggers = random.sample(range(1, 2), random.randint(0, 1))
        CommentThread().update(
            thread_id,
            abuse_flaggers=[str(x) for x in abuse_flaggers],
            historical_abuse_flaggers=[str(x) for x in historical_abuse_flaggers],
        )
        if abuse_flaggers:
            expected_data[thread_author]["active_flags"] += 1
        if historical_abuse_flaggers:
            expected_data[thread_author]["inactive_flags"] += 1

        for _ in range(5):
            comment_author = random.choice(authors)
            expected_data[comment_author]["responses"] += 1
            comment_id = Comment().insert(
                body="This is a test comment",
                course_id=course_id,
                author_id=comment_author,
                comment_thread_id=str(thread_id),
                author_username=comment_author,
            )
            abuse_flaggers_comment = random.sample(range(1, 3), random.randint(0, 2))
            historical_abuse_flaggers_comment = random.sample(
                range(1, 2), random.randint(0, 1)
            )
            Comment().update(
                comment_id,
                abuse_flaggers=[str(x) for x in abuse_flaggers_comment],
                historical_abuse_flaggers=[
                    str(x) for x in historical_abuse_flaggers_comment
                ],
            )
            if abuse_flaggers_comment:
                expected_data[comment_author]["active_flags"] += 1
            if historical_abuse_flaggers_comment:
                expected_data[comment_author]["inactive_flags"] += 1

            for _ in range(3):
                comment = Comment().get(comment_id)
                if not comment:
                    continue
                Comment().update(
                    comment_id,
                    child_count=comment["child_count"],
                )
                reply_author = random.choice(authors)
                expected_data[reply_author]["replies"] += 1
                reply_id = Comment().insert(
                    body="This is a test comment",
                    course_id=course_id,
                    author_id=reply_author,
                    parent_id=comment_id,
                    comment_thread_id=str(thread_id),
                    author_username=reply_author,
                )
                abuse_flaggers_reply = random.sample(range(1, 3), random.randint(0, 2))
                historical_abuse_flaggers_reply = random.sample(
                    range(1, 2), random.randint(0, 1)
                )
                Comment().update(
                    reply_id,
                    abuse_flaggers=[str(x) for x in abuse_flaggers_reply],
                    historical_abuse_flaggers=[
                        str(x) for x in historical_abuse_flaggers_reply
                    ],
                )
                if abuse_flaggers_reply:
                    expected_data[reply_author]["active_flags"] += 1
                if historical_abuse_flaggers_reply:
                    expected_data[reply_author]["inactive_flags"] += 1

    return expected_data


def test_create_user(api_client: APIClient) -> None:
    """Test creating a new user."""
    user_id = "test_id"
    username = "test-user"
    response = api_client.post_json(
        "/api/v2/users", data={"id": user_id, "username": username}
    )
    assert response.status_code == 200
    user = Users().get(user_id)
    assert user
    assert user["username"] == username


def test_create_user_with_existing_id(api_client: APIClient) -> None:
    """Test create user with an existing id."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.post_json(
        "/api/v2/users", data={"id": user_id, "username": "test-user-2"}
    )
    assert response.status_code == 400


def test_create_user_with_existing_username(api_client: APIClient) -> None:
    """Test create user with an existing username."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.post_json(
        "/api/v2/users", data={"id": "test_id_2", "username": username}
    )
    assert response.status_code == 400


def test_update_user(api_client: APIClient) -> None:
    """Test updating user information."""
    user_id = "test_id"
    username = "test-user"
    new_username = "new-test-user"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.put_json(
        f"/api/v2/users/{user_id}", data={"username": new_username}
    )
    assert response.status_code == 200
    user = Users().get(user_id)
    assert user
    assert user["username"] == new_username


def test_update_user_id(api_client: APIClient) -> None:
    """Test updating user id."""
    user_id = "test_id"
    username = "test-user"
    new_id = "new-test-id"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.put_json(f"/api/v2/users/{user_id}", data={"id": new_id})
    assert response.status_code == 200
    user = Users().get(user_id)
    assert user
    assert user["username"] == username


def test_update_non_existent_user(api_client: APIClient) -> None:
    """Test updating non-existent user."""
    user_id = "test_id"
    response = api_client.put_json(
        f"/api/v2/users/{user_id}", data={"username": "new-test-user"}
    )
    assert response.status_code == 200


def test_update_user_with_conflicting_info(api_client: APIClient) -> None:
    """Test updating user with conflicting information."""
    user_id = "test_id"
    username = "test-user"
    conflicting_username = "test-user-2"
    Users().insert(
        user_id,
        username,
    )
    Users().insert(
        "test_id_2",
        conflicting_username,
    )
    response = api_client.put_json(
        f"/api/v2/users/{user_id}", data={"username": conflicting_username}
    )
    assert response.status_code == 400


def test_get_user(api_client: APIClient) -> None:
    """Test getting user information."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.get(f"/api/v2/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["external_id"] == user_id
    assert user["username"] == username


def test_get_non_existent_user(api_client: APIClient) -> None:
    """Test getting non-existent user."""
    user_id = "test_id"
    response = api_client.get(f"/api/v2/users/{user_id}")
    assert response.status_code == 404


def test_get_user_with_no_votes(api_client: APIClient) -> None:
    """Test getting user with no votes."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.get(f"/api/v2/users/{user_id}?complete=true")
    assert response.status_code == 200
    user = response.json()
    assert user["upvoted_ids"] == []


def test_get_user_with_votes(api_client: APIClient) -> None:
    """Test getting user with votes."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    thread_id = CommentThread().insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="author1",
        author_username="author_user",
    )
    thread = CommentThread().get(thread_id)
    user = Users().get(user_id)
    assert thread
    assert user
    upvote_content(
        thread,
        user,
    )
    response = api_client.get(f"/api/v2/users/{user_id}?complete=true")
    assert response.status_code == 200
    user = response.json()
    assert user
    assert user["upvoted_ids"] == [thread_id]


def test_get_active_threads_requires_course_id(api_client: APIClient) -> None:
    """Test getting active threads requires course id."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    setup_10_threads()
    response = api_client.get(f"/api/v2/users/{user_id}/active_threads")
    assert response.status_code == 200
    assert response.json() == {}


def test_get_active_threads(api_client: APIClient) -> None:
    """Test getting active threads."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    setup_10_threads()
    course_id = "course1"
    response = api_client.get(
        f"/api/v2/users/{user_id}/active_threads?course_id={course_id}",
    )
    assert response.status_code == 200
    threads = response.json()["collection"]
    assert len(threads) == 10


def test_marks_thread_as_read_for_user(api_client: APIClient) -> None:
    """Test marking a thread as read for a user."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    thread_id = CommentThread().insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="test_id",
        author_username="test-user",
    )

    thread = CommentThread().get(thread_id)
    assert thread
    response = api_client.post_json(
        f"/api/v2/users/{user_id}/read",
        data={"source_type": "thread", "source_id": thread_id},
    )
    assert response.status_code == 200

    read_date = {}
    updated_user = Users().get(user_id)
    assert updated_user
    read_states = updated_user.get("read_states", [])
    for state in read_states:
        if state["course_id"] == thread["course_id"]:
            read_date = state["last_read_times"]

    assert read_date
    assert read_date.get(thread_id)
    assert read_date[thread_id] >= thread["updated_at"]


def test_replaces_username(api_client: APIClient) -> None:
    """Test replace_username api."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    user = Users().get(user_id)
    assert user
    assert user["username"] == username

    new_username = "test_username_replacement"
    response = api_client.post_json(
        f"/api/v2/users/{user_id}/replace_username", data={"new_username": new_username}
    )
    assert response.status_code == 200
    updated_user = Users().get(user_id)
    assert updated_user
    assert updated_user["username"] == new_username


def test_attempts_to_replace_username_of_non_existent_user(
    api_client: APIClient,
) -> None:
    """Test replace_username api."""
    new_username = "test_username_replacement"
    response = api_client.post_json(
        "/api/v2/users/1234/replace_username", data={"new_username": new_username}
    )
    assert response.status_code == 404


def test_attempts_to_replace_username_and_username_on_content(
    api_client: APIClient,
) -> None:
    """Test replace_username api with content."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    setup_10_threads()
    user = Users().get(user_id)
    new_username = "test_username_replacement"

    response = api_client.post_json(
        f"/api/v2/users/{user_id}/replace_username", data={"new_username": new_username}
    )
    assert response.status_code == 200

    user = Users().get(user_id)
    assert user
    assert user["username"] == new_username
    contents = list(Contents().get_list(author_id=user_id))
    assert len(contents) > 0
    for content in contents:
        assert content["author_username"] == new_username


def test_attempts_to_replace_username_without_sending_new_username(
    api_client: APIClient,
) -> None:
    """Test replace_username api without sending new username."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    response = api_client.post_json(
        f"/api/v2/users/{user_id}/replace_username",
        data={},
    )
    assert response.status_code == 500


def test_attempts_to_retire_user_without_sending_retired_username(
    api_client: APIClient,
) -> None:
    """Test retire user api without sending retired username."""
    user_id = "1"
    response = api_client.post_json(
        f"/api/v2/users/{user_id}/retire",
        data={},
    )
    assert response.status_code == 500


def test_attempts_to_retire_non_existent_user(api_client: APIClient) -> None:
    """Test retire non-existent user."""
    user_id = "1234"
    retired_username = "retired_user_test"
    response = api_client.post_json(
        f"/api/v2/users/{user_id}/retire",
        data={"retired_username": retired_username},
    )
    assert response.status_code == 404


def test_retire_user(api_client: APIClient) -> None:
    """Test retire user."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    setup_10_threads()
    retired_username = "retired_username_ABCD1234"
    user = Users().get(user_id)
    assert user
    assert user["username"] == username

    response = api_client.post_json(
        f"/api/v2/users/{user_id}/retire",
        data={"retired_username": retired_username},
    )
    assert response.status_code == 200
    user = Users().get(user_id)
    assert user
    assert user["username"] == retired_username
    assert user["email"] == ""
    contents = list(Contents().get_list(author_id=user_id))
    assert len(contents) > 0
    for content in contents:
        if content["_type"] == "CommentThread":
            assert content["title"] == RETIRED_TITLE
        assert content["body"] == RETIRED_BODY
        assert content["author_username"] == retired_username


def test_retire_user_with_subscribed_threads(api_client: APIClient) -> None:
    """Test retire user with subscribed threads."""
    user_id = "test_id"
    username = "test-user"
    Users().insert(
        user_id,
        username,
    )
    setup_10_threads()
    retired_username = "retired_username_ABCD1234"
    user = Users().get(user_id)
    assert user
    assert user["username"] == username
    thread_id = CommentThread().insert(
        title="Test Thread",
        body="This is a test thread",
        course_id="course1",
        commentable_id="commentable1",
        author_id="test_id",
        author_username="test-user",
    )
    subscribe_user(user_id, thread_id, "CommentThread")
    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?course_id=course1"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["thread_count"] == 1

    # Retire the user.
    response = api_client.post_json(
        f"/api/v2/users/{user_id}/retire",
        data={"retired_username": retired_username},
    )
    assert response.status_code == 200

    user = Users().get(user_id)
    assert user
    assert user["username"] == retired_username
    assert user["email"] == ""
    # User should be subscribed to no threads.
    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?course_id=course1",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["thread_count"] == 0
    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?course_id=course1",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["thread_count"] == 0

    # User's comments should be blanked out.
    contents = list(Contents().get_list(author_id=user_id))
    assert len(contents) > 0
    for content in contents:
        if content["_type"] == "CommentThread":
            assert content["title"] == RETIRED_TITLE
        assert content["body"] == RETIRED_BODY
        assert content["author_username"] == retired_username


def test_update_user_stats(
    api_client: APIClient,
    build_structure_and_response: dict[str, Any],
) -> None:
    """Test update user stats."""
    course_id = "test_course"
    expected_data = build_structure_and_response
    expected_result = sorted(
        expected_data.values(),
        key=lambda x: (x["threads"], x["responses"], x["replies"]),
        reverse=True,
    )
    response = api_client.get(f"/api/v2/users/{course_id}/stats")
    assert response.status_code == 200
    res = response.json()
    assert res["user_stats"] != expected_result

    response = api_client.post_json(f"/api/v2/users/{course_id}/update_stats", data={})
    assert response.status_code == 200
    res = response.json()
    assert res["user_count"] == 6

    response = api_client.get(f"/api/v2/users/{course_id}/stats")
    assert response.status_code == 200
    res = response.json()
    assert res["user_stats"] == expected_result


def test_returns_users_stats_with_default_activity_sort(
    api_client: APIClient,
    build_structure_and_response: dict[str, Any],
) -> None:
    """Test returns user's stats with default/activity sort."""
    course_id = "test_course"
    expected_data = build_structure_and_response
    expected_result = sorted(
        expected_data.values(),
        key=lambda x: (x["threads"], x["responses"], x["replies"], x["username"]),
        reverse=True,
    )
    response = api_client.post_json(f"/api/v2/users/{course_id}/update_stats", data={})
    assert response.status_code == 200
    res = response.json()
    assert res["user_count"] == 6

    response = api_client.get(f"/api/v2/users/{course_id}/stats")
    assert response.status_code == 200
    res = response.json()
    assert res["user_stats"] == expected_result


def test_handle_stats_for_user_with_no_activity(api_client: APIClient) -> None:
    """Test handle stats for user with no activity."""
    invalid_course_id = "course-v1:edX+DNE+Not_EXISTS"
    response = api_client.get(f"/api/v2/users/{invalid_course_id}/stats")
    assert response.status_code == 200
    res = response.json()
    assert res["user_stats"] == []


def test_returns_users_stats_filtered_by_user_with_default_activity_sort(
    api_client: APIClient,
    build_structure_and_response: dict[str, Any],
) -> None:
    """Test returns user's stats filtered by user with default/activity sort."""
    course_id = "test_course"
    authors = ["author-1", "author-2", "author-3", "author-4", "author-5", "author-6"]
    usernames = random.sample(authors, 2)
    usernames_str = ",".join(usernames)
    full_data = build_structure_and_response
    response = api_client.post_json(f"/api/v2/users/{course_id}/update_stats", data={})
    assert response.status_code == 200
    res = response.json()
    assert res["user_count"] == 6

    expected_result = [
        val for val in full_data.values() if val["username"] in usernames
    ]
    expected_result.sort(key=lambda x: usernames.index(x["username"]))

    response = api_client.get(
        f"/api/v2/users/{course_id}/stats?usernames={usernames_str}",
    )
    assert response.status_code == 200
    res = response.json()
    assert res["user_stats"] == expected_result


def test_returns_users_stats_with_recency_sort(api_client: APIClient) -> None:
    """Test returns user's stats with recency sort."""
    course_id = "test_course"
    response = api_client.post_json(f"/api/v2/users/{course_id}/update_stats", data={})
    response = api_client.get(
        f"/api/v2/users/{course_id}/stats?sort_key=recency&with_timestamps=true"
    )
    assert response.status_code == 200
    res = response.json()
    sorted_order = sorted(
        res["user_stats"],
        key=lambda x: (x["last_activity_at"], x["username"]),
        reverse=True,
    )
    assert res["user_stats"] == sorted_order


def test_returns_users_stats_with_flagged_sort(
    api_client: APIClient,
    build_structure_and_response: dict[str, Any],
) -> None:
    """Test returns user's stats with flagged sort."""
    course_id = "test_course"
    expected_data = build_structure_and_response
    response = api_client.post_json(f"/api/v2/users/{course_id}/update_stats", data={})
    expected_result = sorted(
        expected_data.values(),
        key=lambda x: (x["active_flags"], x["inactive_flags"], x["username"]),
        reverse=True,
    )

    response = api_client.get(f"/api/v2/users/{course_id}/stats?sort_key=flagged")
    assert response.status_code == 200
    res = response.json()
    assert res["user_stats"] == expected_result
