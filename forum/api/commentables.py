"""
Native Python Commenttables APIs.
"""

from forum.backends.mongodb.api import get_commentables_counts_based_on_type


def get_commentables_stats(course_id: str) -> dict[str, int]:
    """
    Get the threads count based on thread_type.

    Parameters:
        course_id: The ID of the course.
    Body:
        Empty.
    Response:
        The threads count for the given course_id based on thread_type.
        e.g.
        reponse = {
                "discussion": 10,
                "question": 20
            }
    """
    return get_commentables_counts_based_on_type(course_id)
