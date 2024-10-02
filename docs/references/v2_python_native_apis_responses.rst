===========================
Python Native API Responses
===========================

This document outlines the structure of responses for various Python native APIs related to comments, threads, and user information in the context of course discussions.

Create Parent Comment(create_parent_comment) API
================================================
Creates a parent comment in the course discussion.

Response Example:
-----------------

.. code-block:: json

   {
       "id": "66eaf98e6592735b5a38129f",
       "body": "<p>parent comment</p>",
       "course_id": "course-v1:Arbisoft+SE002+2024_S2",
       "anonymous": false,
       "anonymous_to_peers": false,
       "created_at": "2024-09-18T16:02:22Z",
       "updated_at": "2024-09-18T16:02:22Z",
       "at_position_list": [],
       "user_id": "8",
       "username": "faraz1",
       "commentable_id": "course",
       "votes": {
           "count": 0,
           "up_count": 0,
           "down_count": 0,
           "point": 0
       },
       "abuse_flaggers": [],
       "edit_history": [],
       "closed": false,
       "type": "comment",
       "endorsed": false,
       "depth": 0,
       "thread_id": "66df3056d77f29ace2ff201d",
       "parent_id": null,
       "child_count": 0
   }

Create Child Comment(create_child_comment) API
==============================================
Creates a child comment in response to a parent comment.

Response Example:
-----------------

.. code-block:: json

   {
       "id": "66eafa538e98584d34d47969",
       "body": "<p>child comment</p>",
       "course_id": "course-v1:Arbisoft+SE002+2024_S2",
       "anonymous": false,
       "anonymous_to_peers": false,
       "created_at": "2024-09-18T16:05:39Z",
       "updated_at": "2024-09-18T16:05:39Z",
       "at_position_list": [],
       "user_id": "8",
       "username": "faraz1",
       "commentable_id": "course",
       "votes": {
           "count": 0,
           "up_count": 0,
           "down_count": 0,
           "point": 0
       },
       "abuse_flaggers": [],
       "edit_history": [],
       "closed": false,
       "type": "comment",
       "endorsed": false,
       "depth": 1,
       "thread_id": "66df3056d77f29ace2ff201d",
       "parent_id": "66eaf98e6592735b5a38129f",
       "child_count": 0
   }

Update Comment(update_comment) API
==================================
Updates the content of an existing comment.

Response Example (Edit Content):
--------------------------------

.. code-block:: json

   {
       "id": "66eaf98e6592735b5a38129f",
       "body": "<p>parent comment editing</p>",
       "course_id": "course-v1:Arbisoft+SE002+2024_S2",
       "anonymous": false,
       "anonymous_to_peers": false,
       "created_at": "2024-09-18T16:02:22Z",
       "updated_at": "2024-09-18T16:07:59Z",
       "at_position_list": [],
       "user_id": "8",
       "username": "faraz1",
       "commentable_id": "course",
       "votes": {
           "count": 0,
           "up_count": 0,
           "down_count": 0,
           "point": 0
       },
       "abuse_flaggers": [],
       "edit_history": [
           {
               "original_body": "<p>parent comment</p>",
               "reason_code": null,
               "editor_username": "faraz1",
               "created_at": "2024-09-18T16:07:59Z"
           }
       ],
       "closed": false,
       "type": "comment",
       "endorsed": false,
       "depth": 0,
       "thread_id": "66df3056d77f29ace2ff201d",
       "parent_id": null,
       "child_count": 1,
       "endorsement": null
   }

Response Example (Endorse Comment):
-----------------------------------

.. code-block:: json

   {
       "id": "66eaf98e6592735b5a38129f",
       "body": "<p>parent comment editing</p>",
       "course_id": "course-v1:Arbisoft+SE002+2024_S2",
       "anonymous": false,
       "anonymous_to_peers": false,
       "created_at": "2024-09-18T16:02:22Z",
       "updated_at": "2024-09-18T16:08:51Z",
       "at_position_list": [],
       "user_id": "8",
       "username": "faraz1",
       "commentable_id": "course",
       "votes": {
           "count": 0,
           "up_count": 0,
           "down_count": 0,
           "point": 0
       },
       "abuse_flaggers": [],
       "edit_history": [
           {
               "original_body": "<p>parent comment</p>",
               "reason_code": null,
               "editor_username": "faraz1",
               "created_at": "2024-09-18T16:07:59Z"
           }
       ],
       "closed": false,
       "type": "comment",
       "endorsed": true,
       "depth": 0,
       "thread_id": "66df3056d77f29ace2ff201d",
       "parent_id": null,
       "child_count": 1,
       "endorsement": {
           "user_id": "8",
           "time": "2024-09-18T16:08:51Z"
       }
   }

Get Commentables Stats(get_commentables_stats) API
==================================================
Returns the statistics for the commentable objects in a course.

Response Example:
-----------------

.. code-block:: json

   {
       "course": {
           "discussion": 1,
           "question": 1
       }
   }

Get Parent Comment(get_parent_comment) API
==========================================
Retrieves a parent comment in the course discussion.

Response Example (Endorsed):
----------------------------

.. code-block:: json

   {
       "id": "66eaf98e6592735b5a38129f",
       "body": "<p>parent comment editing</p>",
       "course_id": "course-v1:Arbisoft+SE002+2024_S2",
       "anonymous": false,
       "anonymous_to_peers": false,
       "created_at": "2024-09-18T16:02:22Z",
       "updated_at": "2024-09-18T16:08:51Z",
       "at_position_list": [],
       "user_id": "8",
       "username": "faraz1",
       "commentable_id": "course",
       "votes": {
           "count": 0,
           "up_count": 0,
           "down_count": 0,
           "point": 0
       },
       "abuse_flaggers": [],
       "edit_history": [
           {
               "original_body": "<p>parent comment</p>",
               "reason_code": null,
               "editor_username": "faraz1",
               "created_at": "2024-09-18T16:07:59Z"
           }
       ],
       "closed": false,
       "type": "comment",
       "endorsed": true,
       "depth": 0,
       "thread_id": "66df3056d77f29ace2ff201d",
       "parent_id": null,
       "child_count": 1,
       "endorsement": {
           "user_id": "8",
           "time": "2024-09-18T16:08:51Z"
       }
   }

Response Example (Not Endorsed):
--------------------------------

.. code-block:: json

   {
       "id": "66eaf98e6592735b5a38129f",
       "body": "<p>parent comment editing</p>",
       "course_id": "course-v1:Arbisoft+SE002+2024_S2",
       "anonymous": false,
       "anonymous_to_peers": false,
       "created_at": "2024-09-18T16:02:22Z",
       "updated_at": "2024-09-18T16:21:00Z",
       "at_position_list": [],
       "user_id": "8",
       "username": "faraz1",
       "commentable_id": "course",
       "votes": {
           "count": 0,
           "up_count": 0,
           "down_count": 0,
           "point": 0
       },
       "abuse_flaggers": [],
       "edit_history": [
           {
               "original_body": "<p>parent comment</p>",
               "reason_code": null,
               "editor_username": "faraz1",
               "created_at": "2024-09-18T16:07:59Z"
           }
       ],
       "closed": false,
       "type": "comment",
       "endorsed": false,
       "depth": 0,
       "thread_id": "66df3056d77f29ace2ff201d",
       "parent_id": null,
       "child_count": 1
   }

Get User(get_user) API
======================

The `get_user` API retrieves user-specific data such as their username, followed threads, and upvoted content.

**Response Example:**

.. code-block:: json

    {
        "id": "8",
        "username": "faraz1",
        "external_id": "8",
        "subscribed_thread_ids": ["66df3056d77f29ace2ff201d", "66df1595a3a68c001d742c05"],
        "subscribed_commentable_ids": [],
        "subscribed_user_ids": [],
        "follower_ids": [],
        "upvoted_ids": ["66df1595a3a68c001d742c05", "66df3056d77f29ace2ff201d"],
        "downvoted_ids": [],
        "default_sort_key": "date"
    }

Pin Thread(pin_thread) API
==========================

The `pin_thread` API pins a discussion thread at the top for users to easily access.

**Response Example:**

.. code-block:: json

    {
        "id": "66df1595a3a68c001d742c05",
        "body": "<p>test question&nbsp;</p>",
        "course_id": "course-v1:Arbisoft+SE002+2024_S2",
        "anonymous": False,
        "anonymous_to_peers": False,
        "created_at": "2024-09-09T15:34:45Z",
        "updated_at": "2024-09-18T16:27:05Z",
        "at_position_list": [],
        "user_id": "8",
        "username": "faraz1",
        "commentable_id": "course",
        "votes": {
            "count": 1,
            "up_count": 1,
            "down_count": 0,
            "point": 1
        },
        "abuse_flaggers": [],
        "edit_history": [],
        "closed": False,
        "type": "thread",
        "thread_type": "question",
        "title": "test question",
        "context": "course",
        "last_activity_at": "2024-09-18T09:19:38Z",
        "closed_by": None,
        "tags": [],
        "group_id": None,
        "pinned": True
    }

Unpin Thread(unpin_thread) API
==============================

The `unpin_thread` API unpins a previously pinned thread, removing its elevated visibility.

**Response Example:**

.. code-block:: json

    {
        "id": "66df1595a3a68c001d742c05",
        "body": "<p>test question&nbsp;</p>",
        "course_id": "course-v1:Arbisoft+SE002+2024_S2",
        "anonymous": False,
        "anonymous_to_peers": False,
        "created_at": "2024-09-09T15:34:45Z",
        "updated_at": "2024-09-18T16:27:49Z",
        "at_position_list": [],
        "user_id": "8",
        "username": "faraz1",
        "commentable_id": "course",
        "votes": {
            "count": 1,
            "up_count": 1,
            "down_count": 0,
            "point": 1
        },
        "abuse_flaggers": [],
        "edit_history": [],
        "closed": False,
        "type": "thread",
        "thread_type": "question",
        "title": "test question",
        "context": "course",
        "last_activity_at": "2024-09-18T09:19:38Z",
        "closed_by": None,
        "tags": [],
        "group_id": None,
        "pinned": False
    }
