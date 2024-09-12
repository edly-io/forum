"""
Test Search Thread API Endpoints

By default, the test cases use fixtures and do not hit the actual Elasticsearch instance.
However, it is recommended to use the actual Elasticsearch for verifying all tests.

To do so, update the following configurations:

- Set FORUM_ENABLE_ELASTIC_SEARCH=True in forum.settings.test.py.
- Update FORUM_ELASTIC_SEARCH_CONFIG based on your Elasticsearch instance. By default, it queries localhost:5000.
To test it quickly, you can create a new container with the same image as the production instance.

Run this command to start Elasticsearch on localhost:5000.
Note: Update the image i.e elasticsearch:7.17.13 as used in production

```
docker run --rm --name elasticsearch_test -p 5200:9200 -p 5300:9300 -e \
"discovery.type=single-node" elasticsearch:7.17.13
```
"""

import time
import urllib.parse
from typing import Any, Optional
from unittest.mock import patch

import pytest
from django.conf import settings
from requests import Response

from forum.models import Comment, CommentThread, Users
from forum.models.model_utils import mark_as_read
from forum.search.backend import ElasticsearchBackend
from forum.search.comment_search import ThreadSearch
from test_utils.client import APIClient


@pytest.fixture(autouse=True)
def initialize_indices() -> None:
    """Initialize Elasticsearch indices if Elasticsearch is enabled."""
    if settings.FORUM_ENABLE_ELASTIC_SEARCH:
        es = ElasticsearchBackend()
        es.client.indices.delete(index="*")
        es.initialize_indices()


def assert_result_total(response: Response, expected_total: int) -> None:
    """Assert that the total number of results matches the expected total."""
    assert response.status_code == 200
    result = response.json()
    assert result["total_results"] == expected_total


def get_search_response(
    api_client: APIClient,
    query_string: str,
    get_thread_ids_value: Optional[list[str]] = None,
    get_suggested_text_value: Optional[str] = "",
    get_therad_ids_with_corrected_text_values: Optional[list[str]] = None,
) -> Response:
    """
    Helper function to patch ThreadSearch methods and get search response.

    :param api_client: The API client used to make the request.
    :param query_string: The query string for the search.
    :param get_thread_ids_value: Mocked return value for get_thread_ids.
    :param get_suggested_text_value: Mocked return value for get_suggested_text.
    :param get_therad_ids_with_corrected_text_values: Mocked return value for get_thread_ids_with_corrected_text.
    :return: The response from the search request.
    """

    get_thread_ids_value = get_thread_ids_value or []
    get_therad_ids_with_corrected_text_values = (
        get_therad_ids_with_corrected_text_values or []
    )

    if not settings.FORUM_ENABLE_ELASTIC_SEARCH:
        with patch.object(
            ThreadSearch, "get_thread_ids", return_value=get_thread_ids_value
        ):
            with patch.object(
                ThreadSearch,
                "get_suggested_text",
                return_value=get_suggested_text_value,
            ):
                with patch.object(
                    ThreadSearch,
                    "get_thread_ids_with_corrected_text",
                    return_value=get_therad_ids_with_corrected_text_values,
                ):
                    return api_client.get_json(
                        f"/api/v2/search/threads?{query_string}", {}
                    )

    return api_client.get_json(f"/api/v2/search/threads?{query_string}", {})


def refresh_elastic_search_indices() -> None:
    """Refresh Elasticsearch indices."""
    if settings.FORUM_ENABLE_ELASTIC_SEARCH:
        ElasticsearchBackend().refresh_indices()


def test_invalid_request(api_client: APIClient) -> None:
    """
    Test that invalid requests to the search API return a 400 status.

    This test checks that invalid parameters in the search query string
    result in a 400 Bad Request response.
    """

    user_id = "1"
    course_id = "course-v1:Arbisoft+SE002+2024_S2"

    Users().insert(user_id, username="user1", email="email1")
    comment_thread_id = CommentThread().insert(
        title="title",
        body="Hello World!",
        pinned=False,
        author_id=user_id,
        course_id=course_id,
        commentable_id="66b4e0440dead7001deb948b",
        author_username="Faraz",
    )
    Comment().insert(
        body="Hello World!",
        course_id=course_id,
        comment_thread_id=comment_thread_id,
        author_id="1",
        author_username="Faraz",
    )

    refresh_elastic_search_indices()

    params = {"course_id": course_id}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string)
    assert response.status_code == 400

    params = {"text": "foobar", "sort_key": "invalid"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string)
    assert response.status_code == 400


def test_search_returns_empty_for_deleted_thread(api_client: APIClient) -> None:
    """
    Test that searching for a deleted thread returns no results.

    This test checks that after a thread is deleted, it no longer appears
    in search results.
    """

    course_id = "course-v1:Arbisoft+SE002+2024_S2"
    thread_id = CommentThread().insert(
        title="title-1",
        course_id=course_id,
        body="body-1",
        author_id="1",
        author_username="test_user",
        commentable_id="course",
    )

    CommentThread().delete(thread_id)

    refresh_elastic_search_indices()

    params = {"course_id": course_id, "text": "title-1", "sort_key": "date"}
    query_string = urllib.parse.urlencode(params)

    response = get_search_response(api_client, query_string, [], "")

    assert_result_total(response, 0)


def test_search_returns_only_updated_thread(api_client: APIClient) -> None:
    """
    Test that searching for a thread returns only the updated version.

    This test checks that after a thread is updated, the search results reflect
    the updated title and not the original one.
    """

    original_title = "title-original"
    updated_title = "updated-title"
    course_id = "course-v1:Arbisoft+SE002+2024_S2"

    thread_id = CommentThread().insert(
        title=original_title,
        course_id=course_id,
        body="body-1",
        author_id="1",
        author_username="test_user",
        commentable_id="course",
    )
    CommentThread().update(thread_id=thread_id, title=updated_title)

    refresh_elastic_search_indices()

    params = {"course_id": course_id, "text": original_title}
    query_string = urllib.parse.urlencode(params)

    response = get_search_response(api_client, query_string, [], "")
    assert_result_total(response, 0)

    params = {"course_id": course_id, "text": updated_title}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, [thread_id], "")
    assert_result_total(response, 1)


def test_search_returns_empty_for_deleted_comment(api_client: APIClient) -> None:
    """
    Test that searching for a deleted comment returns no results.

    This test checks that after a comment is deleted, it no longer appears
    in search results.
    """

    course_id = "course-v1:Arbisoft+SE002+2024_S2"
    thread_id = CommentThread().insert(
        title="thread-1",
        course_id=course_id,
        body="thread-body",
        author_id="1",
        author_username="test_user",
        commentable_id="course",
    )
    comment_id = Comment().insert(
        body="comment-body",
        course_id=course_id,
        comment_thread_id=thread_id,
        author_id="1",
    )
    Comment().delete(comment_id)

    refresh_elastic_search_indices()

    params = {"course_id": course_id, "text": "comment-body", "sort_key": "date"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, [], "")

    assert_result_total(response, 0)


def test_search_returns_only_updated_comment(api_client: APIClient) -> None:
    """
    Test that searching for a comment returns only the updated version.

    This test checks that after a comment is updated, the search results reflect
    the updated text and not the original one.
    """

    original_comment = "comment-original"
    updated_comment = "comment-updated"
    course_id = "course-v1:Arbisoft+SE002+2024_S2"

    thread_id = CommentThread().insert(
        title="thread-1",
        course_id=course_id,
        body="thread-body",
        author_id="1",
        author_username="test_user",
        commentable_id="course",
    )
    comment_id = Comment().insert(
        body=original_comment,
        course_id=course_id,
        comment_thread_id=thread_id,
        author_id="1",
    )

    Comment().update(comment_id=comment_id, body=updated_comment)
    refresh_elastic_search_indices()

    params = {"course_id": course_id, "text": original_comment}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, [], "")
    assert_result_total(response, 0)

    params = {"course_id": course_id, "text": updated_comment}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, [thread_id], "")
    assert_result_total(response, 1)


def create_threads_and_comments_for_filter_tests(
    course_id_0: str, course_id_1: str
) -> tuple[list[str], dict[str, Any]]:
    """
    Create a set of threads and comments for testing various filter conditions.
    Returns a list of thread IDs and a dictionary mapping thread IDs to their associated comment IDs.
    """
    threads_ids = []
    threads_comments: dict[str, Any] = {}
    for i in range(35):
        context = "standalone" if i > 29 else "course"
        group_id = i % 5
        thread_id = CommentThread().insert(
            title=f"title-{i}",
            body="text",
            author_id="1",
            course_id=course_id_0 if i % 2 == 0 else course_id_1,
            commentable_id=f"commentable{i % 3}",
            context=context,
            group_id=group_id,
        )
        threads_ids.append(thread_id)

        if i < 2:
            comment_id = Comment().insert(
                body="objectionable",
                course_id=course_id_0 if i % 2 == 0 else course_id_1,
                comment_thread_id=thread_id,
                author_id="1",
            )
            Comment().update(comment_id=comment_id, abuse_flaggers=["1"])
            comment_ids = threads_comments.get(thread_id, [])
            comment_ids.append(comment_id)
            threads_comments[thread_id] = comment_ids

        if i in [0, 2, 4]:
            CommentThread().update(thread_id=thread_id, thread_type="question")
            comment_id = Comment().insert(
                body="response",
                course_id=course_id_0 if i % 2 == 0 else course_id_1,
                comment_thread_id=thread_id,
                author_id="1",
            )
            comment_ids = threads_comments.get(thread_id, [])
            comment_ids.append(comment_id)
            threads_comments[thread_id] = comment_ids

    return threads_ids, threads_comments


# The test covers all the filters and making this modular leads to more complex structure.
# pylint: disable=too-many-statements
def test_filter_threads(api_client: APIClient) -> None:
    """
    Test various filtering options for threads, including course_id, context, flagged, unanswered, group_id,
    commentable_id, and combinations of these filters. Asserts that the correct threads are returned for each filter.
    """
    course_id_0 = "course-v1:Arbisoft+SE002+2024_S2"
    course_id_1 = "course-v1:Arbisoft+SE003+2024_S2"

    user_id = Users().insert("1", username="user1", email="example@test.com")
    threads_ids, threads_comments = create_threads_and_comments_for_filter_tests(
        course_id_0, course_id_1
    )

    refresh_elastic_search_indices()

    # Test filtering by course_id
    def assert_response_contains(
        response: Response, expected_indexes: list[int]
    ) -> None:
        assert response.status_code == 200
        threads = response.json()["collection"]
        expected_ids = {threads_ids[i] for i in expected_indexes}
        actual_ids = {thread["id"] for thread in threads}
        assert (
            actual_ids == expected_ids
        ), f"Expected {expected_ids}, but got {actual_ids}"

    # Test filtering by course_id
    params = {"text": "text", "course_id": course_id_0}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[:30:2])
    assert_response_contains(response, [i for i in range(30) if i % 2 == 0])

    # # Test filtering by context
    params = {"text": "text", "context": "standalone"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[30:35])
    assert_response_contains(response, list(range(30, 35)))

    # Test filtering with unread filter
    user = Users().get(_id=user_id) or {}
    thread = CommentThread().get(_id=threads_ids[0]) or {}
    mark_as_read(user, thread)
    params = {
        "text": "text",
        "course_id": course_id_0,
        "user_id": user_id,
        "unread": "True",
    }
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[:35:2])
    assert_response_contains(response, [i for i in range(1, 30) if i % 2 == 0])

    # Test filtering with flagged filter
    params = {"text": "text", "course_id": course_id_0, "flagged": "True"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[:30:2])
    assert_response_contains(response, [0])

    # Test filtering with unanswered filter
    params = {"text": "text", "course_id": course_id_0, "unanswered": "True"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[:30:2])
    assert_response_contains(response, [0, 2, 4])

    # Test filtering with unanswered filter and group_id
    params = {
        "text": "text",
        "course_id": course_id_0,
        "unanswered": "True",
        "group_id": "2",
    }
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[:30:2])
    assert_response_contains(response, [0, 2])

    params = {
        "text": "text",
        "course_id": course_id_0,
        "unanswered": "True",
        "group_id": "4",
    }
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[:30:2])
    assert_response_contains(response, [0, 4])

    comment = threads_comments[threads_ids[4]][0]
    Comment().update(comment_id=comment, endorsed=True)
    refresh_elastic_search_indices()

    response = get_search_response(api_client, query_string, threads_ids[:30:2])
    assert_response_contains(response, [0])

    # Test filtering by commentable_id
    params = {"text": "text", "commentable_id": "commentable0"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[::3])
    assert_response_contains(response, [i for i in range(30) if i % 3 == 0])

    # Test filtering by commentable_ids
    params = {"text": "text", "commentable_ids": "commentable0,commentable1"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(
        api_client, query_string, [threads_ids[i] for i in range(35) if i % 3 in [0, 1]]
    )
    assert_response_contains(response, [i for i in range(30) if i % 3 in [0, 1]])

    # Test filtering by group_id
    params = {"text": "text", "group_id": "1"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids)
    assert_response_contains(response, [i for i in range(30) if i % 5 in [0, 1]])

    # Test filtering by group_ids
    params = {"text": "text", "group_ids": "1,2"}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids)
    assert_response_contains(response, [i for i in range(30) if i % 5 in [0, 1, 2]])

    # Test filtering by all filters combined
    params = {
        "text": "text",
        "course_id": course_id_0,
        "commentable_id": "commentable0",
        "group_id": "1",
    }
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, threads_ids[::6])
    assert_response_contains(response, [0, 6])


def test_pagination(api_client: APIClient) -> None:
    """
    Test pagination of search results. Ensures that results are correctly paginated and that the order of
    threads is as expected across different pages.
    """
    course_id = "course-v1:Arbisoft+SE002+2024_S2"

    threads_ids = []
    for i in range(50):
        thread_id = CommentThread().insert(
            title=f"title-{i}",
            body="text",
            author_id="1",
            course_id=course_id,
            commentable_id="dummy",
        )
        threads_ids.append(thread_id)
        # Add a slight delay to ensure created_date is different
        time.sleep(0.001)

    refresh_elastic_search_indices()

    def check_pagination(per_page: Optional[int], num_pages: int) -> None:
        result_ids = []
        params = {"text": "text"}
        if per_page:
            params["per_page"] = str(per_page)

        for i in range(1, num_pages + 2):
            params["page"] = str(i)
            query_string = urllib.parse.urlencode(params)
            response = get_search_response(api_client, query_string, threads_ids)
            assert response.status_code == 200
            result = response.json()
            result_ids.extend([r["id"] for r in result["collection"]])

        expected_ids = threads_ids[::-1]
        assert result_ids == expected_ids

    check_pagination(1, 50)
    check_pagination(30, 2)
    check_pagination(None, 3)


def test_sorting(api_client: APIClient) -> None:
    """
    Test the sorting functionality for threads based on various criteria, such as date, activity, votes, and comments.
    Asserts that the threads are sorted correctly according to the specified sorting key.
    """
    course_id = "course-v1:Arbisoft+SE002+2024_S2"

    # Create and save threads
    threads_ids = []
    for i in range(6):
        thread = CommentThread().insert(
            title=f"title-{i}",
            body="text",
            author_id="1",
            course_id=course_id,
            commentable_id="dummy",
        )
        threads_ids.append(thread)
        # Add a slight delay to ensure created_date is different
        time.sleep(0.001)

    # Update specific threads to simulate activity, votes, and comments
    votes = CommentThread().get_votes_dict(up=["1"], down=[])
    CommentThread().update(thread_id=threads_ids[1], votes=votes)
    CommentThread().update(thread_id=threads_ids[2], votes=votes)
    CommentThread().update(thread_id=threads_ids[1], comments_count=5)
    CommentThread().update(thread_id=threads_ids[3], comments_count=5)

    refresh_elastic_search_indices()

    def fetch_and_check(sort_key: Optional[str], expected_indexes: list[int]) -> None:
        params = {"text": "text"}
        if sort_key:
            params["sort_key"] = str(sort_key)

        query_string = urllib.parse.urlencode(params)
        response = get_search_response(api_client, query_string, threads_ids)
        assert_result_total(response, 6)
        result = response.json()
        threads = result["collection"]
        expected_ids = [threads_ids[i] for i in expected_indexes]
        actual_ids = [thread["id"] for thread in threads]
        assert (
            actual_ids == expected_ids
        ), f"Expected {expected_ids}, but got {actual_ids}"

    # Test various sorting scenarios
    fetch_and_check("date", [5, 4, 3, 2, 1, 0])
    fetch_and_check("activity", [5, 4, 3, 2, 1, 0])
    fetch_and_check("votes", [2, 1, 5, 4, 3, 0])
    fetch_and_check("comments", [3, 1, 5, 4, 2, 0])
    fetch_and_check(None, [5, 4, 3, 2, 1, 0])  # Default sorting by date


def test_spelling_correction(api_client: APIClient) -> None:
    """
    Test the spelling correction feature in search.
    Verifies that misspelled words in both thread titles and comment bodies are correct
    """
    commentable_id = "test_commentable"
    thread_title = "a thread about green artichokes"
    comment_body = "a comment about greed pineapples"

    thread_id = CommentThread().insert(
        title=thread_title,
        body="",
        author_id="1",
        course_id="course_id",
        commentable_id=commentable_id,
    )

    Comment().insert(
        body=comment_body,
        course_id="course_id",
        comment_thread_id=thread_id,
        author_id="1",
    )
    refresh_elastic_search_indices()

    def get_threda_ids_for_fixtures(original_text: str) -> list[str]:
        """ """
        if original_text in thread_title or original_text in comment_body:
            return [thread_id]
        else:
            return []

    def check_correction(original_text: str, corrected_text: Optional[str]) -> None:
        params = {"text": original_text}
        query_string = urllib.parse.urlencode(params)
        get_thread_ids_value = get_threda_ids_for_fixtures(original_text)
        response = get_search_response(
            api_client,
            query_string,
            get_thread_ids_value,
            corrected_text,
            [thread_id] if corrected_text else [],
        )
        assert response.status_code == 200
        result = response.json()
        assert (
            result.get("corrected_text") == corrected_text
        ), f"Expected '{corrected_text}', but got '{result.get('corrected_text')}'"
        assert result[
            "collection"
        ], f"Expected non-empty collection for '{original_text}', but got empty."

    # Test: can correct a word appearing only in a comment
    check_correction("pinapples", "pineapples")

    # Test: can correct a word appearing only in a thread
    check_correction("arichokes", "artichokes")

    # Test: can correct a word appearing in both a comment and a thread
    check_correction("abot", "about")

    # Test: can correct a word with multiple errors
    check_correction("artcokes", "artichokes")

    # Test: can correct misspellings in different terms in the same search
    check_correction("comment abot pinapples", "comment about pineapples")

    # Test: does not correct a word that appears in a thread but has a correction and no matches in comments
    check_correction("green", None)

    # Test: does not correct a word that appears in a comment but has a correction and no matches in threads
    check_correction("greed", None)


def test_spelling_correction_with_mush_clause(api_client: APIClient) -> None:
    """
    Test the spelling correction feature & mush clause in the search.
    Verifies the even if the text matches with the threds it should also consider other
    params in the search i.e course_id
    """
    course_id = "course_id"

    # Add documents containing a word that is close to our search term
    # but that do not match our filter criteria; because we currently only
    # consider the top suggestion returned by Elasticsearch without regard
    # to the filter, and that suggestion in this case does not match any
    # results, we should get back no results and no correction.
    for _ in range(10):
        CommentThread().insert(
            title="abbot",
            body="text",
            author_id="1",
            course_id="other_course_id",
            commentable_id="other_commentable_id",
        )
    refresh_elastic_search_indices()

    params = {"text": "abot", "course_id": course_id}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(
        api_client,
        query_string,
    )
    assert response.status_code == 200
    result = response.json()
    corrected_text = result.get("corrected_text")
    assert (
        corrected_text is None
    ), f"Expected 'corrected_text' to be None, but got a value '{corrected_text}'."
    assert not result["collection"], "Expected an empty collection, but got results."


def test_total_results_and_num_pages(api_client: APIClient) -> None:
    """
    Test the total number of results and pagination of search results.
    Ensures that the total count of search results and the number of pages are calculated
    correctly based on varying text patterns in threads.
    """
    course_id = "test/course/id"

    threads_ids = []

    # Creating 100 comments with varying text patterns
    for i in range(1, 101):
        text = "all"
        if i % 2 == 0:
            text += " half"
        if i % 4 == 0:
            text += " quarter"
        if i % 10 == 0:
            text += " tenth"
        if i == 100:
            text += " one"

        # Create the comment
        thread_id = CommentThread().insert(
            title=f"title-{i}",
            body=text,
            course_id=course_id,
            author_id="1",
            commentable_id="course",
        )
        threads_ids.append(thread_id)

    # Refresh Elasticsearch indices to ensure all comments are searchable
    refresh_elastic_search_indices()

    def get_thread_ids_for_fixture(text: str) -> list[str]:
        """
        Get thread_ids for the fixtures.
        """
        if text == "all":
            return threads_ids
        elif text == "half":
            return threads_ids[::2]
        elif text == "quarter":
            return threads_ids[::4]
        elif text == "tenth":
            return threads_ids[::10]
        elif text == "one":
            return threads_ids[::100]
        return []

    def test_text(
        text: str, expected_total_results: int, expected_num_pages: int
    ) -> None:
        params = {"course_id": course_id, "text": text, "per_page": "10"}
        query_string = urllib.parse.urlencode(params)
        get_thread_ids_value = get_thread_ids_for_fixture(text)
        response = get_search_response(api_client, query_string, get_thread_ids_value)
        assert response.status_code == 200
        result = response.json()
        assert (
            result["total_results"] == expected_total_results
        ), f"Expected total_results {expected_total_results}, but got {result['total_results']}"
        assert (
            result["num_pages"] == expected_num_pages
        ), f"Expected num_pages {expected_num_pages}, but got {result['num_pages']}"

    # Running the tests
    test_text("all", 100, 10)
    test_text("half", 50, 5)
    test_text("quarter", 25, 3)
    test_text("tenth", 10, 1)
    test_text("one", 1, 1)


def test_unicode_data(api_client: APIClient) -> None:
    """
    Test the handling of Unicode characters in search queries. Verifies that threads containing Unicode characters
    are searchable and return correct results when queried with ASCII search terms.
    """
    text = "␎ⶀⅰ⑀⍈┣♲⺝"
    search_term = "artichoke"

    # Create a comment thread and a comment containing the specified text
    thread_id = CommentThread().insert(
        title="A thread title",
        body=f"{search_term} {text}",
        author_id="1",
        course_id="course-v1:Arbisoft+SE002+2024_S2",
        commentable_id="course",
    )
    Comment().insert(
        body=text,
        course_id="course-v1:Arbisoft+SE002+2024_S2",
        comment_thread_id=thread_id,
        author_id="1",
    )

    # Refresh Elasticsearch indices to make the new data searchable
    refresh_elastic_search_indices()

    # Perform the search with the ASCII term
    params = {"course_id": "course-v1:Arbisoft+SE002+2024_S2", "text": search_term}
    query_string = urllib.parse.urlencode(params)
    response = get_search_response(api_client, query_string, [thread_id])

    # Check that the response is OK and that exactly one result is returned
    assert response.status_code == 200
    json = response.json()["collection"]
    assert len(json) == 1, f"Expected 1 result, but got {len(json)}"
