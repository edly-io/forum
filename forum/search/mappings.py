"""
This module defines the Elasticsearch mappings for the forum application.
"""

from typing import Any

FORUM_ES_CONFIGURATIONS: list[dict[str, Any]] = [
    {
        "index_name": "comments",
        "mapping": {
            "dynamic": "false",
            "properties": {
                "body": {
                    "type": "text",
                    "store": True,
                    "term_vector": "with_positions_offsets",
                },
                "course_id": {"type": "keyword"},
                "comment_thread_id": {"type": "keyword"},
                "commentable_id": {"type": "keyword"},
                "group_id": {"type": "keyword"},
                "context": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "title": {"type": "keyword"},
            },
        },
    },
    {
        "index_name": "comment_threads",
        "mapping": {
            "dynamic": "false",
            "properties": {
                "title": {
                    "type": "text",
                    "boost": 5.0,
                    "store": True,
                    "term_vector": "with_positions_offsets",
                },
                "body": {
                    "type": "text",
                    "store": True,
                    "term_vector": "with_positions_offsets",
                },
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "last_activity_at": {"type": "date"},
                "comment_count": {"type": "integer"},
                "votes_point": {"type": "integer"},
                "context": {"type": "keyword"},
                "course_id": {"type": "keyword"},
                "commentable_id": {"type": "keyword"},
                "author_id": {"type": "keyword"},
                "group_id": {"type": "integer"},
                "id": {"type": "keyword"},
                "thread_id": {"type": "keyword"},
            },
        },
    },
]


def get_mapping_by_index_name(index_name: str) -> dict[str, Any]:
    """
    Retrieves the mapping configuration for a given index name from the predefined configurations.
    """
    for config in FORUM_ES_CONFIGURATIONS:
        if config["index_name"] == index_name:
            return config["mapping"]
    raise ValueError("Invalid index_name")
