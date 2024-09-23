"""Test commentables count api endpoint."""

import random
import uuid

from forum.backends.mongodb import CommentThread
from test_utils.client import APIClient


def test_get_commentables_counts_api(api_client: APIClient) -> None:
    """
    Test retrieving counts of discussion and question threads for multiple commentables within a course.
    """
    course_id = "abcd"
    id_map = {}

    for _ in range(5):
        commentable_id = str(uuid.uuid4())
        question_count = random.randint(5, 15)
        discussion_count = random.randint(5, 15)

        for _ in range(question_count):
            CommentThread().insert(
                title="Question Thread",
                body="This is a question thread.",
                course_id=course_id,
                commentable_id=commentable_id,
                thread_type="question",
                author_id="test_user_id",
                author_username="test_user",
                abuse_flaggers=[],
                historical_abuse_flaggers=[],
            )

        for _ in range(discussion_count):
            CommentThread().insert(
                title="Discussion Thread",
                body="This is a discussion thread.",
                course_id=course_id,
                commentable_id=commentable_id,
                thread_type="discussion",
                author_id="test_user_id",
                author_username="test_user",
                abuse_flaggers=[],
                historical_abuse_flaggers=[],
            )

        id_map[commentable_id] = {
            "question": question_count,
            "discussion": discussion_count,
        }

    response = api_client.get_json(f"/api/v2/commentables/{course_id}/counts", {})

    assert response.status_code == 200
    assert response.json() == id_map
