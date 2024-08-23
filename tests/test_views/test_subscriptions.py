"""Tests for subscription apis."""

from forum.models import CommentThread, Subscriptions, Users
from test_utils.client import APIClient


def test_get_subscribed_threads(api_client: APIClient) -> None:
    """
    Test getting subscribed threads for a user.
    """
    user_id = "1"
    course_id = "demo_course"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )

    Subscriptions().insert(user_id, comment_thread_id, source_type="CommentThread")
    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?course_id={course_id}"
    )
    assert response.status_code == 200
    threads = response.json()["collection"]
    assert len(threads) == 1
    assert threads[0]["id"] == comment_thread_id


def test_get_subscribed_threads_with_filters(api_client: APIClient) -> None:
    """
    Test getting subscribed threads for a user with filters.
    """
    user_id = "1"
    course_id = "demo_course"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    Subscriptions().insert(user_id, comment_thread_id, source_type="thread")

    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?flagged=true&course_id={course_id}"
    )
    assert response.status_code == 200
    threads = response.json()["collection"]
    assert len(threads) == 0

    CommentThread().update(comment_thread_id, abuse_flaggers=[user_id])
    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?flagged=true&course_id={course_id}"
    )
    assert response.status_code == 200
    threads = response.json()["collection"]
    assert len(threads) == 1
    assert threads[0]["id"] == comment_thread_id


def test_subscribe_thread(api_client: APIClient) -> None:
    """
    Test subscribing to a thread.
    """
    user_id = "1"
    course_id = "demo_course"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    response = api_client.post(
        f"/api/v2/users/{user_id}/subscriptions",
        data={"source_type": "thread", "source_id": comment_thread_id},
    )
    assert response.status_code == 200
    subscription = Subscriptions().get_subscription(user_id, comment_thread_id)
    assert subscription is not None


def test_unsubscribe_thread(api_client: APIClient) -> None:
    """
    Test unsubscribing from a thread.
    """
    user_id = "1"
    course_id = "demo_course"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    Subscriptions().insert(user_id, comment_thread_id, source_type="thread")

    response = api_client.delete(
        f"/api/v2/users/{user_id}/subscriptions?source_id={comment_thread_id}"
    )
    assert response.status_code == 200
    subscription = Subscriptions().get_subscription(user_id, comment_thread_id)
    assert subscription is None

    # Attempt to unsubscribe from a thread that the user is not subscribed to
    response = api_client.delete(
        f"/api/v2/users/{user_id}/subscriptions?source_id={comment_thread_id}"
    )
    assert response.status_code == 404


def test_get_subscribed_threads_with_pagination(api_client: APIClient) -> None:
    """
    Test getting subscribed threads for a user with pagination.
    """
    user_id = "1"
    course_id = "demo_course"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    comment_thread_id_2 = CommentThread().insert(
        "Thread 2",
        "Body 2",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    comment_thread_id_3 = CommentThread().insert(
        "Thread 2",
        "Body 2",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    Subscriptions().insert(user_id, comment_thread_id, source_type="thread")
    Subscriptions().insert(user_id, comment_thread_id_2, source_type="thread")
    Subscriptions().insert(user_id, comment_thread_id_3, source_type="thread")

    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?page=1&per_page=2&course_id={course_id}"
    )
    assert response.status_code == 200
    threads = response.json()["collection"]
    assert len(threads) == 2
    assert threads[0]["id"] in [
        comment_thread_id,
        comment_thread_id_2,
        comment_thread_id_3,
    ]

    response = api_client.get(
        f"/api/v2/users/{user_id}/subscribed_threads?page=2&per_page=2&course_id={course_id}"
    )
    assert response.status_code == 200
    threads = response.json()["collection"]
    assert len(threads) == 1
    assert threads[0]["id"] in [
        comment_thread_id,
        comment_thread_id_2,
        comment_thread_id_3,
    ]


def test_get_thread_subscriptions(api_client: APIClient) -> None:
    """
    Test getting subscriptions of a thread.
    """
    user_id = "1"
    course_id = "demo_course"
    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    subscription_id = Subscriptions().insert(
        user_id, comment_thread_id, source_type="CommentThread"
    )

    response = api_client.get(
        f"/api/v2/threads/{comment_thread_id}/subscriptions?page=1"
    )
    assert response.status_code == 200
    subscriptions = response.json()["collection"]
    assert len(subscriptions) == 1
    assert subscriptions[0]["id"] == subscription_id

    response = api_client.get(
        f"/api/v2/threads/{comment_thread_id}/subscriptions?page=2"
    )
    assert response.status_code == 200
    subscriptions = response.json()["collection"]
    assert len(subscriptions) == 0


def test_get_thread_subscriptions_with_pagination(api_client: APIClient) -> None:
    """
    Test getting subscriptions of a thread with pagination.
    """
    user_id = "1"
    course_id = "demo_course"
    comment_thread_id = CommentThread().insert(
        "Thread 1",
        "Body 1",
        course_id,
        "CommentThread",
        "3",
        "user3",
    )
    user_ids = ["1", "2", "3", "4", "5"]
    for user_id in user_ids:
        Users().insert(
            user_id,
            username=f"user{user_id}",
            email=f"email{user_id}@example.com",
        )
        Subscriptions().insert(user_id, comment_thread_id, source_type="CommentThread")

    response = api_client.get(
        f"/api/v2/threads/{comment_thread_id}/subscriptions?page=1&per_page=2"
    )
    assert response.status_code == 200
    subscriptions = response.json()["collection"]
    assert len(subscriptions) == 2
    assert subscriptions[0]["subscriber_id"] == user_ids[0]
    assert subscriptions[1]["subscriber_id"] == user_ids[1]

    response = api_client.get(
        f"/api/v2/threads/{comment_thread_id}/subscriptions?page=2&per_page=2"
    )
    assert response.status_code == 200
    subscriptions = response.json()["collection"]
    assert len(subscriptions) == 2
    assert subscriptions[0]["subscriber_id"] == user_ids[2]
    assert subscriptions[1]["subscriber_id"] == user_ids[3]

    response = api_client.get(
        f"/api/v2/threads/{comment_thread_id}/subscriptions?page=3&per_page=2"
    )
    assert response.status_code == 200
    subscriptions = response.json()["collection"]
    assert len(subscriptions) == 1
    assert subscriptions[0]["subscriber_id"] == user_ids[4]
