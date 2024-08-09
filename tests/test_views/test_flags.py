from unittest.mock import patch, Mock


def test_comment_flag_api(api_client, users_model, content_model):
    """
    Test the comment flag API.

    This test checks that a user can flag a comment for abuse and then unflag it.
    """
    user_id = users_model.collection.insert_one({"_id": "1"}).inserted_id
    comment_id = content_model.collection.insert_one(
        {
            "_id": "66ace22474ba69001e1440bd",
            "abuse_flaggers": [],
            "author_id": "2",
            "historical_abuse_flaggers": [],
            "visible": True,
        }
    ).inserted_id

    # Test flagging comment for abuse
    mock_users_class = Mock(return_value=users_model)
    mock_contents_class = Mock(return_value=content_model)
    with patch("forum.models.users.Users", new=mock_users_class):
        with patch("forum.models.contents.Contents", new=mock_contents_class):
            response = api_client.put(
                path=f"/api/v2/comments/{comment_id}/abuse_flag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment = content_model.collection.find_one({"_id": comment_id})
            assert comment["abuse_flaggers"] == [str(user_id)]

            response = api_client.put(
                path=f"/api/v2/comments/{comment_id}/abuse_unflag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment = content_model.collection.find_one({"_id": comment_id})
            assert comment["abuse_flaggers"] == []


def test_comment_flag_api_invalid_data(api_client, users_model, content_model):
    """
    Test the comment flag API with invalid data.

    This test checks that the API returns a 400 error when the user or comment does not exist.
    """
    user_id = users_model.collection.insert_one({"_id": "1"}).inserted_id
    mock_users_class = Mock(return_value=users_model)
    mock_contents_class = Mock(return_value=content_model)
    with patch("forum.models.users.Users", new=mock_users_class):
        with patch("forum.models.contents.Contents", new=mock_contents_class):
            response = api_client.put(
                path="/api/v2/comments/2/abuse_flag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 400
            assert response.data == {"error": "User / Comment doesn't exist"}


def test_comment_thread_api(api_client, users_model, content_model):
    """
    Test the comment thread flag API.

    This test checks that a user can flag a comment thread for abuse and then unflag it.
    """
    user_id = users_model.collection.insert_one({"_id": "1"}).inserted_id
    comment_thread_id = content_model.collection.insert_one(
        {
            "_id": "66ace22474ba69001e1440cd",
            "abuse_flaggers": [],
            "author_id": "3",
            "historical_abuse_flaggers": [],
            "visible": True,
        }
    ).inserted_id

    mock_users_class = Mock(return_value=users_model)
    mock_contents_class = Mock(return_value=content_model)
    with patch("forum.models.users.Users", new=mock_users_class):
        with patch("forum.models.contents.Contents", new=mock_contents_class):
            response = api_client.put(
                f"/api/v2/threads/{comment_thread_id}/abuse_flag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment_thread = content_model.collection.find_one(
                {"_id": comment_thread_id},
            )
            assert comment_thread["abuse_flaggers"] == [str(user_id)]

            response = api_client.put(
                path=f"/api/v2/comments/{comment_thread_id}/abuse_unflag",
                data={"user_id": str(user_id)},
            )
            assert response.status_code == 200
            comment = content_model.collection.find_one({"_id": comment_thread_id})
            assert comment["abuse_flaggers"] == []
