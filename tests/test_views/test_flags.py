"""Test flags api endpoints."""

from forum.models import Comment, CommentThread, Users
from test_utils.client import APIClient


def test_comment_thread_api(api_client: APIClient) -> None:
    """
    Test the comment thread flag API.

    This test checks that a user can flag a comment thread for abuse and then unflag it.
    """
    user_id = "1"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        "_type",
        "CommentThread",
        "1",
        "user1",
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
    )

    response = api_client.put_json(
        f"/api/v2/threads/{comment_thread_id}/abuse_flag",
        data={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    comment_thread = response.json()
    assert comment_thread["abuse_flaggers"] == [str(user_id)]

    response = api_client.put_json(
        path=f"/api/v2/threads/{comment_thread_id}/abuse_unflag",
        data={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    comment = CommentThread().get(comment_thread_id)
    assert comment is not None
    assert comment["abuse_flaggers"] == []


def test_comment_flag_api(api_client: APIClient) -> None:
    """
    Test the comment flag API.

    This test checks that a user can flag a comment for abuse and then unflag it.
    """
    user_id = "1"
    comment_thread_id = "66ace22474ba69001e1440cd"
    author_id = "4"
    author_username = "edly"
    course_id = "course-xyz"
    Users().insert(user_id, username="user1", email="email1")
    comment_id = Comment().insert(
        "<p>Comment 1</p>",
        course_id,
        comment_thread_id,
        author_id,
        author_username,
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
    )
    response = api_client.put_json(
        f"/api/v2/comments/{comment_id}/abuse_flag",
        data={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    comment_thread = response.json()
    assert comment_thread["abuse_flaggers"] == [str(user_id)]

    response = api_client.put_json(
        path=f"/api/v2/comments/{comment_id}/abuse_unflag",
        data={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    comment = Comment().get(comment_id)
    assert comment is not None
    assert comment["abuse_flaggers"] == []

    response = api_client.put_json(
        path=f"/api/v2/comments/{comment_id}/abuse_unflag",
        data={"user_id": str(user_id)},
    )
    assert response.status_code == 200
    comment = Comment().get(comment_id)
    assert comment is not None
    assert comment["abuse_flaggers"] == []


def test_comment_flag_api_invalid_data(api_client: APIClient) -> None:
    """
    Test the comment flag API with invalid data.

    This test checks that the API returns a 400 error when the user or comment does not exist.
    """
    user_id = "1"
    Users().insert(user_id, username="user1", email="email1")

    response = api_client.put_json(
        path="/api/v2/comments/66ace22474ba69001e1440bd/abuse_flag",
        data={"user_id": str(user_id)},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "User / Comment doesn't exist"}
