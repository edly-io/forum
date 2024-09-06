"""Test flags api endpoints."""

from bson import ObjectId

from forum.models import Comment, CommentThread, Users
from test_utils.client import APIClient


def test_comment_thread_api(api_client: APIClient) -> None:
    """
    Test the comment thread flag API.

    This test checks that a user can flag a comment thread for abuse and then unflag it.
    """
    flag_user = str(ObjectId())
    author_user = str(ObjectId())
    Users().insert(flag_user, flag_user)
    Users().insert(author_user, author_user)
    comment_thread_id = CommentThread().insert(
        title="Thread 1",
        body="Body 1",
        course_id="course1",
        commentable_id="3",
        author_id=author_user,
        author_username=author_user,
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
    )

    response = api_client.put_json(
        f"/api/v2/threads/{comment_thread_id}/abuse_flag",
        data={"user_id": str(flag_user)},
    )
    assert response.status_code == 200
    comment_thread = response.json()
    assert comment_thread["abuse_flaggers"] == [str(flag_user)]

    response = api_client.put_json(
        path=f"/api/v2/threads/{comment_thread_id}/abuse_unflag",
        data={"user_id": str(flag_user)},
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
    flag_user = str(ObjectId())
    author_user = str(ObjectId())
    Users().insert(flag_user, flag_user)
    Users().insert(author_user, author_user)
    comment_thread_id = str(ObjectId())
    course_id = "course-xyz"
    comment_id = Comment().insert(
        "<p>Comment 1</p>",
        course_id,
        author_user,
        comment_thread_id=comment_thread_id,
        author_username=author_user,
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
    )

    response = api_client.put_json(
        f"/api/v2/comments/{comment_id}/abuse_flag",
        data={"user_id": str(flag_user)},
    )
    assert response.status_code == 200
    comment_thread = response.json()
    assert comment_thread["abuse_flaggers"] == [str(flag_user)]

    response = api_client.put_json(
        path=f"/api/v2/comments/{comment_id}/abuse_unflag",
        data={"user_id": str(flag_user)},
    )
    assert response.status_code == 200
    comment = Comment().get(comment_id)
    assert comment is not None
    assert comment["abuse_flaggers"] == []

    response = api_client.put_json(
        path=f"/api/v2/comments/{comment_id}/abuse_unflag",
        data={"user_id": str(flag_user)},
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
    user = str(ObjectId())
    Users().insert(user, user)

    response = api_client.put_json(
        path="/api/v2/comments/66ace22474ba69001e1440bd/abuse_flag",
        data={"user_id": str(user)},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "User / Comment doesn't exist"}
