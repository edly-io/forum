"""Tests for Users apis."""

from forum.constants import RETIRED_BODY, RETIRED_TITLE
from forum.backends.mongodb import Comment, CommentThread, Contents, Users
from forum.backends.mongodb.api import subscribe_user, upvote_content
from test_utils.client import APIClient


def setup_10_threads(author_id: str, author_username: str) -> list[str]:
    """Create 10 threads for a user."""
    ids = []
    for thread in range(10):
        thread_id = CommentThread().insert(
            title=f"Test Thread {thread}",
            body="This is a test thread",
            course_id="course1",
            commentable_id="commentable1",
            author_id=author_id,
            author_username=author_username,
        )
        Comment().insert(
            body="This is a test comment",
            course_id="course1",
            author_id=author_id,
            comment_thread_id=str(thread_id),
            author_username=author_username,
        )
        ids.append(thread_id)
    return ids


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
    setup_10_threads(user_id, username)
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
    setup_10_threads(user_id, username)
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
    setup_10_threads(user_id, username)
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
    setup_10_threads(user_id, username)
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
    setup_10_threads(user_id, username)
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
