"""Test flags api endpoints."""

from unittest.mock import Mock, patch

from django.test import Client

from forum.models.contents import Contents
from forum.models.users import Users


def test_comment_thread_api(api_client: Client, users_model: Users, content_model: Contents) -> None:
    """
    Test the comment thread flag API.

    This test checks that a user can flag a comment thread for abuse and then unflag it.
    """
    user_id = "1"
    comment_thread_id = "66ace22474ba69001e1440cd"
    users_model.insert(user_id, username="user1", email="email1")
    content_model.insert(
        comment_thread_id,
        "3",
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
        visible=True,
    )
    mock_users_class = Mock(return_value=users_model)
    mock_contents_class = Mock(return_value=content_model)
    with patch("forum.models.users.Users", new=mock_users_class):
        with patch("forum.models.contents.Contents", new=mock_contents_class):
            response = api_client.put(
                f"/api/v2/threads/{comment_thread_id}/abuse_flag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment_thread = response.json()
            assert comment_thread["abuse_flaggers"] == [str(user_id)]

            response = api_client.put(
                path=f"/api/v2/threads/{comment_thread_id}/abuse_unflag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment = content_model.get(comment_thread_id)
            assert comment is not None
            assert comment["abuse_flaggers"] == []


def test_comment_flag_api(api_client: Client, users_model: Users, content_model: Contents) -> None:
    """
    Test the comment flag API.

    This test checks that a user can flag a comment for abuse and then unflag it.
    """
    user_id = "1"
    comment_id = "66ace22474ba69001e1440cd"
    users_model.insert(user_id, username="user1", email="email1")
    content_model.insert(
        comment_id,
        "3",
        abuse_flaggers=[],
        historical_abuse_flaggers=[],
        visible=True,
    )
    mock_users_class = Mock(return_value=users_model)
    mock_contents_class = Mock(return_value=content_model)
    with patch("forum.models.users.Users", new=mock_users_class):
        with patch("forum.models.contents.Contents", new=mock_contents_class):
            response = api_client.put(
                f"/api/v2/comments/{comment_id}/abuse_flag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment_thread = response.json()
            assert comment_thread["abuse_flaggers"] == [str(user_id)]

            response = api_client.put(
                path=f"/api/v2/comments/{comment_id}/abuse_unflag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment = content_model.get(comment_id)
            assert comment is not None
            assert comment["abuse_flaggers"] == []

            response = api_client.put(
                path=f"/api/v2/comments/{comment_id}/abuse_unflag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment = content_model.get(comment_id)
            assert comment is not None
            assert comment["abuse_flaggers"] == []


def test_comment_flag_api_invalid_data(api_client: Client, users_model: Users, content_model: Contents) -> None:
    """
    Test the comment flag API with invalid data.

    This test checks that the API returns a 400 error when the user or comment does not exist.
    """
    user_id = "1"
    users_model.insert(user_id, username="user1", email="email1")
    mock_users_class = Mock(return_value=users_model)
    mock_contents_class = Mock(return_value=content_model)
    with patch("forum.models.users.Users", new=mock_users_class):
        with patch("forum.models.contents.Contents", new=mock_contents_class):
            response = api_client.put(
                path="/api/v2/comments/66ace22474ba69001e1440bd/abuse_flag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 400
            assert response.json() == {"error": "User / Comment doesn't exist"}
