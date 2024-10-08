"""Test comments api endpoints."""

from forum.backends.mongodb import Comment, CommentThread, Users
from test_utils.client import APIClient


def setup_models() -> tuple[str, str, str]:
    """
    Setup models.

    This will create a user, thread and parent comment
    for being used in comments api tests.
    """

    user_id = "1"
    username = "user1"
    course_id = "course-xyz"
    Users().insert(user_id, username=username, email="email1")
    comment_thread_id = CommentThread().insert(
        title="Thread 1",
        body="Thread 1",
        course_id=course_id,
        commentable_id="CommentThread",
        author_id=user_id,
        author_username=username,
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
    )
    parent_comment_id = Comment().insert(
        body="<p>Parent Comment</p>",
        course_id=course_id,
        author_id=user_id,
        comment_thread_id=comment_thread_id,
        author_username=username,
    )
    return user_id, comment_thread_id, parent_comment_id


def test_comment_post_api(api_client: APIClient) -> None:
    """
    Test creating a new child comment.
    """

    user_id, thread_id, parent_comment_id = setup_models()

    response = api_client.post_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={
            "body": "<p>Child Comment 1</p>",
            "course_id": "course-xyz",
            "user_id": user_id,
        },
    )
    assert response.status_code == 200
    comment = response.json()
    assert comment["body"] == "<p>Child Comment 1</p>"
    assert comment["user_id"] == user_id
    assert comment["thread_id"] == thread_id
    assert comment["parent_id"] == parent_comment_id
    parent_comment = Comment().get(parent_comment_id)
    assert parent_comment is not None
    assert parent_comment["child_count"] == 1


def test_get_comment_api(api_client: APIClient) -> None:
    """
    Test retrieving a single parent comment.
    """
    _, _, parent_comment_id = setup_models()

    response = api_client.get_json(f"/api/v2/comments/{parent_comment_id}", {})
    assert response.status_code == 200
    comment = response.json()
    assert comment["body"] == "<p>Parent Comment</p>"
    assert comment["endorsed"] is False
    assert comment["id"] == parent_comment_id
    assert comment["votes"]["point"] == 0
    assert comment["depth"] == 0
    assert comment["parent_id"] is None
    assert comment["child_count"] == 0


def test_update_comment_endorsed_api(api_client: APIClient) -> None:
    """
    Test updating the endorsed status of a parent comment.
    """
    user_id, _, parent_comment_id = setup_models()

    response = api_client.put_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={"endorsed": "True", "endorsement_user_id": user_id},
    )
    assert response.status_code == 200
    comment = Comment().get(parent_comment_id)
    assert comment is not None
    assert comment["endorsed"] is True
    assert comment["endorsement"]["user_id"] == user_id

    response = api_client.put_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={"endorsed": "False"},
    )
    assert response.status_code == 200
    comment = Comment().get(parent_comment_id)
    assert comment is not None
    assert comment["endorsed"] is False
    assert comment["endorsement"] is None


def test_delete_parent_comment(api_client: APIClient) -> None:
    """
    Test deleting a comment.
    """

    user_id, _, parent_comment_id = setup_models()

    response = api_client.post_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={
            "body": "<p>Child Comment 1</p>",
            "course_id": "course-xyz",
            "user_id": user_id,
        },
    )
    assert response.status_code == 200
    response = api_client.delete_json(f"/api/v2/comments/{parent_comment_id}")
    assert response.status_code == 200
    assert Comment().get(parent_comment_id) is None


def test_delete_child_comment(api_client: APIClient) -> None:
    """
    Test creating a new child comment.
    """

    user_id, _, parent_comment_id = setup_models()

    response = api_client.post_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={
            "body": "<p>Child Comment 1</p>",
            "course_id": "course-xyz",
            "user_id": user_id,
        },
    )
    assert response.status_code == 200
    child_comment_id = response.json()["id"]
    assert child_comment_id is not None

    parent_comment = Comment().get(parent_comment_id) or {}
    previous_child_count = parent_comment.get("child_count")

    response = api_client.delete_json(f"/api/v2/comments/{child_comment_id}")
    assert previous_child_count is not None
    assert response.status_code == 200
    assert Comment().get(child_comment_id) is None

    parent_comment = Comment().get(parent_comment_id) or {}
    new_child_count = parent_comment.get("child_count")

    assert new_child_count is not None
    assert new_child_count == previous_child_count - 1


def test_returns_400_when_comment_does_not_exist(api_client: APIClient) -> None:
    incorrect_comment_id = "66c42d4aa3a68c001c6c22db"
    response = api_client.get_json(f"/api/v2/comments/{incorrect_comment_id}", {})
    assert response.status_code == 400

    assert response.json() == {
        "error": f"Comment does not exist with Id: {incorrect_comment_id}"
    }

    response = api_client.put_json(
        f"/api/v2/comments/{incorrect_comment_id}", data={"body": "new_body"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": f"Comment does not exist with Id: {incorrect_comment_id}"
    }

    response = api_client.delete_json(f"/api/v2/comments/{incorrect_comment_id}")
    assert response.status_code == 400
    assert response.json() == {
        "error": f"Comment does not exist with Id: {incorrect_comment_id}"
    }


def test_updates_body_correctly(api_client: APIClient) -> None:
    """
    Test updating the body of a comment.
    """
    _, _, parent_comment_id = setup_models()
    comment = Comment().get(parent_comment_id)
    assert comment is not None
    original_body = comment["body"]
    editing_user_id = "2"
    editing_username = "user2"
    Users().insert(editing_user_id, username=editing_username, email="email2")
    edit_reason_code = "test_reason"
    new_body = "new body"
    response = api_client.put_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={
            "body": new_body,
            "editing_user_id": editing_user_id,
            "edit_reason_code": edit_reason_code,
        },
    )

    assert response.status_code == 200
    updated_comment = Comment().get(parent_comment_id)
    assert updated_comment is not None
    assert updated_comment["body"] == new_body
    edit_history = updated_comment["edit_history"]
    assert len(edit_history) == 1
    assert edit_history[0]["original_body"] == original_body
    assert edit_history[0]["reason_code"] == edit_reason_code
    assert edit_history[0]["editor_username"] == editing_username


def test_updates_body_correctly_without_user_id(api_client: APIClient) -> None:
    """
    Test updating the body of a comment without user id.
    """

    _, _, parent_comment_id = setup_models()
    new_body = "new body"
    response = api_client.put_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={"body": new_body},
    )
    assert response.status_code == 200
    updated_comment = Comment().get(parent_comment_id)
    assert updated_comment is not None
    assert updated_comment["body"] == new_body
    assert ("edit_history" not in updated_comment) is True


def test_update_endorsed_and_body_simultaneously(api_client: APIClient) -> None:
    """
    Test updating the body and endorse status of a comment simultaneously.
    """

    _, _, parent_comment_id = setup_models()
    new_body = "new body"
    response = api_client.put_json(
        f"/api/v2/comments/{parent_comment_id}",
        data={"endorsed": "True", "body": new_body},
    )
    assert response.status_code == 200
    updated_comment = Comment().get(parent_comment_id)
    assert updated_comment is not None
    assert updated_comment["body"] == new_body
    assert updated_comment["endorsement"] is None
    assert updated_comment["endorsed"] is True


def test_thread_comment_post_api(api_client: APIClient) -> None:
    """
    Test creating a new parent comment.
    """

    user_id, thread_id, _ = setup_models()

    response = api_client.post_json(
        f"/api/v2/threads/{thread_id}/comments",
        data={
            "body": "<p>Child Comment 1</p>",
            "course_id": "course-xyz",
            "user_id": user_id,
        },
    )
    assert response.status_code == 200
    comment = response.json()
    assert comment["body"] == "<p>Child Comment 1</p>"
    assert comment["user_id"] == user_id
    assert comment["thread_id"] == thread_id
    assert comment["parent_id"] is None
    parent_comment = Comment().get(comment["id"])
    assert parent_comment is not None
    assert parent_comment["child_count"] == 0
