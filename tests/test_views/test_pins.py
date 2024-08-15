"""Test pin/unpin thread api endpoints."""

from unittest.mock import Mock, patch

from forum.models import Comment, CommentThread, Users

from test_utils.client import APIClient


def test_pin_and_unpin_thread_api(api_client: APIClient) -> None:
    """
    Test the pin/unpin thread API.
    This test checks that a user can pin/unpin a thread.
    """
    user_id = "unique_1"

    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        title="title",
        body="Hello World!",
        pinned=False,
        author_id=user_id,
        course_id="course-v1:Arbisoft+SE002+2024_S2",
        commentable_id="66b4e0440dead7001deb948b",
        author_username="Faraz",
    )
    Comment().insert(
        body="Hello World!",
        course_id="course-v1:Arbisoft+SE002+2024_S2",
        comment_thread_id=comment_thread_id,
        author_id="1",
        author_username="Faraz",
    )
    mock_users_class = Mock(return_value=Users())
    mock_thread_class = Mock(return_value=CommentThread())
    mock_comment_class = Mock(return_value=Comment())

    with patch("forum.models.Users", new=mock_users_class):
        with patch("forum.models.CommentThread", new=mock_thread_class):
            with patch("forum.models.Comment", new=mock_comment_class):
                response = api_client.put_json(
                    f"/api/v2/threads/{comment_thread_id}/pin",
                    data={"user_id": user_id},
                )
                assert response.status_code == 200
                thread_data = response.json()
                assert thread_data is not None
                assert thread_data["pinned"] is True
                thread = CommentThread().get(comment_thread_id)
                assert thread is not None
                assert thread["pinned"] is True

                response = api_client.put_json(
                    f"/api/v2/threads/{comment_thread_id}/unpin",
                    data={"user_id": user_id},
                )
                assert response.status_code == 200
                thread_data = response.json()
                assert thread_data is not None
                assert thread_data["pinned"] is False
                thread = CommentThread().get(comment_thread_id)
                assert thread is not None
                assert thread["pinned"] is False


def test_pin_unpin_thread_api_invalid_data(api_client: APIClient) -> None:
    """
    Test the invalid data for pin/unpin thread API.
    This test checks that if user/thread exists or not.
    """
    user_id = "1"
    Users().insert(user_id, username="user1", email="email1")

    mock_users_class = Mock(return_value=Users())
    mock_thread_class = Mock(return_value=CommentThread())

    with patch("forum.models.Users", new=mock_users_class):
        with patch("forum.models.CommentThread", new=mock_thread_class):
            response = api_client.put_json(
                path="/api/v2/threads/66b4e0440dead7001deb948b/pin",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 400
            assert response.json() == {"error": "User / Thread doesn't exist"}

            response = api_client.put_json(
                path="/api/v2/threads/66b4e0440dead7001deb948b/unpin",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 400
            assert response.json() == {"error": "User / Thread doesn't exist"}
