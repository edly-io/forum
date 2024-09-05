Forum v1 MongoDB Document
=========================

Overview
--------

In MongoDB, it maintain three key collections: ``contents``, ``users``, and ``subscriptions``. Each of these collections stores different aspects of data related to the forum system. Below is a detailed exploration of each collection and its associated data models.

Contents Collection
-------------------

The ``contents`` collection in MongoDB stores information about various models, including ``CommentThread``, ``Comment``, and ``EditHistory``. Below is a breakdown of the data fields and relationships associated with these models.

EditHistory
^^^^^^^^^^^

The ``EditHistory`` model represents the history of edits made to comments or threads within the forum system. It manages edit records, including timestamps, edit reasons, and related user information.

Fields
~~~~~~

* **_id** (ObjectId): Unique identifier for the edit history object, self-generated.
* **created_at** (datetime): Timestamp when the edit was made.
* **author_id** (str): ID of the user who made the edit.
* **editor_username** (str): Username of the editor.
* **reason_code** (str): Reason code for the edit.
* **original_body** (str): Original content before the edit.

**Example EditHistory Data**:

.. code-block:: python

    {
        '_id': ObjectId('66d840dba3a68c001d742bd9'),
        'original_body': '<p>post</p>',
        'reason_code': None,
        'editor_username': 'faraz1',
        'author_id': '8',
        'created_at': datetime.datetime(2024, 9, 4, 11, 13, 31, 724000)
    }

Relationships
~~~~~~~~~~~~~

* **Comment**: Each ``EditHistory`` record is associated with a ``Comment``, tracking changes to specific comments.
* **User**: Linked to the user who made the edit, aiding in auditing and managing user actions.

CommentThread
^^^^^^^^^^^^^

The ``CommentThread`` model represents a discussion thread within the forum, managing associated comments and activities.

Fields
~~~~~~

* **_id** (ObjectId): Unique identifier for the thread.
* **votes** (dict): Structure for vote details.
    * **up** (list[str]): User IDs who upvoted.
    * **down** (list[str]): User IDs who downvoted.
    * **up_count** (int): Number of upvotes.
    * **down_count** (int): Number of downvotes.
    * **count** (int): Total votes (up + down).
    * **point** (int): Total points from votes (up - down).
* **visible** (bool): Visibility of the thread, default is True.
* **abuse_flaggers** (list[str]): User IDs who flagged the thread as abusive.
* **historical_abuse_flaggers** (list[str]): User IDs who previously flagged the thread as abusive.
* **thread_type** (str): Type of thread, default is "discussion".
* **context** (str): Context of the thread, default is "course".
* **comment_count** (int): Number of comments, incremented or decremented as comments are added or deleted.
* **at_position_list** (list[dict]): List of positions in the thread.
    * **position** (int): Position in the thread.
    * **content** (str): Content at the position.
* **title** (str): Title of the thread.
* **body** (str): Body content of the thread.
* **course_id** (str): ID of the course to which the thread belongs.
* **commentable_id** (str): ID of the commentable entity, default is "course".
* **_type** (str): Type of content, possible values are "CommentThread" and "Comment".
* **anonymous** (bool): Whether the thread is anonymous, default is False.
* **anonymous_to_peers** (bool): Whether the thread is anonymous to peers, default is False.
* **closed** (bool): Whether the thread is closed, default is False.
* **author_id** (str): ID of the user who created the thread.
* **author_username** (str): Username of the user who created the thread.
* **updated_at** (datetime): Timestamp of the last update.
* **created_at** (datetime): Timestamp when the thread was created.
* **last_activity_at** (datetime): Timestamp of the last activity on the thread.
* **edit_history** (dict): History of edits associated with the thread.
    * **_id** (ObjectId): The Id of the edit_history object, it's self-generated..
    * **created_at** (datetime): The timestamp when the edit was made.
    * **author_id** (str): The ID of the user who made the edit.
    * **editor_username** (str): The username of the editor.
    * **reason_code** (str): The reason code for the edit.
    * **original_body** (str): The original content of the comment or thread before the edit.

**Example CommentThread Data**:

.. code-block:: python

    {
        '_id': ObjectId('66d840b7a3a68c001d742bd5'),
        'votes': {'up': [],
        'down': [],
        'up_count': 0,
        'down_count': 0,
        'count': 0,
        'point': 0},
        'visible': True,
        'abuse_flaggers': [],
        'historical_abuse_flaggers': [],
        'thread_type': 'discussion',
        'context': 'course',
        'comment_count': 2,
        'at_position_list': [],
        'title': 'post editing',
        'body': '<p>post&nbsp;editing</p>',
        'course_id': 'course-v1:Arbisoft+SE002+2024_S2',
        'commentable_id': 'course',
        '_type': 'CommentThread',
        'anonymous': False,
        'anonymous_to_peers': False,
        'closed': False,
        'author_id': '8',
        'author_username': 'faraz1',
        'updated_at': datetime.datetime(2024, 9, 4, 11, 13, 31, 724000),
        'created_at': datetime.datetime(2024, 9, 4, 11, 12, 55, 601000),
        'last_activity_at': datetime.datetime(2024, 9, 4, 11, 13, 18, 26000),
        'edit_history': [
            {
                '_id': ObjectId('66d840dba3a68c001d742bd9'),
                'original_body': '<p>post</p>',
                'reason_code': None,
                'editor_username': 'faraz1',
                'author_id': '8',
                'created_at': datetime.datetime(2024, 9, 4, 11, 13, 31, 724000)
            }
        ]
    }

Relationships
~~~~~~~~~~~~~

* **Comments**: A ``CommentThread`` can have multiple associated ``Comment`` documents.
* **Courses**: The ``course_id`` field links to a ``Course`` model.
* **Subscriptions**: The ``subscriptions`` method retrieves subscriptions related to the thread.
* **Users**: The ``subscribers`` method provides a list of users subscribed to the thread.

Comment
^^^^^^^

The ``Comment`` model represents a comment in the forum system, managing the creation, updating, and deletion of comments.

Types
~~~~~

A ``Comment`` can be either a parent comment or a child comment, depending on the presence of a ``parent_id``.

Fields
~~~~~~

* **_id** (ObjectId): Unique identifier for the comment.
* **votes** (dict): Structure for vote details.
    * **up** (list[str]): User IDs who upvoted.
    * **down** (list[str]): User IDs who downvoted.
    * **up_count** (int): Number of upvotes.
    * **down_count** (int): Number of downvotes.
    * **count** (int): Total votes (up + down).
    * **point** (int): Total points from votes (up - down).
* **visible** (bool): Whether the comment is visible, default is True.
* **abuse_flaggers** (list[str]): User IDs who flagged the comment as abusive.
* **historical_abuse_flaggers** (list[str]): User IDs who previously flagged the comment as abusive.
* **parent_ids** (list[ObjectId]): List of parent comment IDs for nested comments.
* **at_position_list** (list[dict]): List of positions in the comment.
* **body** (str): Body content of the comment.
* **course_id** (str): ID of the course to which the comment belongs.
* **_type** (str): Type of content, possible values are "CommentThread" and "Comment".
* **endorsed** (bool): Whether the comment is endorsed.
* **anonymous** (bool): Whether the comment is anonymous, default is False.
* **anonymous_to_peers** (bool): Whether the comment is anonymous to peers, default is False.
* **author_id** (str): ID of the user who created the comment.
* **comment_thread_id** (str): ID of the parent ``CommentThread``.
* **child_count** (int): Number of child comments.
* **depth** (int): Depth of the comment in the thread hierarchy.
* **author_username** (str): Username of the user who created the comment.
* **created_at** (datetime): Timestamp when the comment was created.
* **updated_at** (datetime): Timestamp when the comment was last updated.
* **endorsement** (dict | None): Endorsement details, if any. It exists only in case of parent commentm if endorsed.
    * **endorsement_user_id** (Optional[str]): The ID of the user who endorsed the comment.
    * **time** (str): The time at which comment is endorsed.
* **sk** (Optional[str]): Sorting key.
* **closed** (bool): Whether the comment is closed, default is False.
* **edit_history** (dict): History of edits associated with the comment.
    * **_id** (ObjectId): The Id of the edit_history object, it's self-generated..
    * **created_at** (datetime): The timestamp when the edit was made.
    * **author_id** (str): The ID of the user who made the edit.
    * **editor_username** (str): The username of the editor.
    * **reason_code** (str): The reason code for the edit.
    * **original_body** (str): The original content of the comment or thread before the edit.

**Example Parent Comment Data**:

.. code-block:: python

    {
        '_id': ObjectId('66d840c4a3a68c001d742bd7'),
        'votes': {
            'up': [],
            'down': [],
            'up_count': 0,
            'down_count': 0,
            'count': 0,
            'point': 0
        },
        'visible': True,
        'abuse_flaggers': [],
        'historical_abuse_flaggers': [],
        'parent_ids': [],
        'at_position_list': [],
        'body': '<p>parent comment 1&nbsp;editing</p>',
        'course_id': 'course-v1:Arbisoft+SE002+2024_S2',
        '_type': 'Comment',
        'endorsed': True,
        'anonymous': False,
        'anonymous_to_peers': False,
        'author_id': '8',
        'comment_thread_id': ObjectId('66d840b7a3a68c001d742bd5'),
        'child_count': 1,
        'depth': 0,
        'author_username': 'faraz1',
        'sk': '66d840c4a3a68c001d742bd7',
        'updated_at': datetime.datetime(2024, 9, 4, 11, 13, 48, 219000),
        'created_at': datetime.datetime(2024, 9, 4, 11, 13, 8, 179000),
        'edit_history': [
            {
                '_id': ObjectId('66d840e3a3a68c001d742bda'),
                'original_body': '<p>parent comment 1</p>',
                'reason_code': None,
                'editor_username': 'faraz1',
                'author_id': '8',
                'created_at': datetime.datetime(2024, 9, 4, 11, 13, 39, 821000)
            }
        ],
        'endorsement': {
            'user_id': '8',
            'time': datetime.datetime(2024, 9, 4, 11, 13, 48, 212000)
        }
    }

**Example Child Comment Data**:

.. code-block:: python

    {
        '_id': ObjectId('66d840cea3a68c001d742bd8'),
        'votes': {
            'up': [],
            'down': [],
            'up_count': 0,
            'down_count': 0,
            'count': 0,
            'point': 0
        },
        'visible': True,
        'abuse_flaggers': [],
        'historical_abuse_flaggers': [],
        'parent_ids': [ObjectId('66d840c4a3a68c001d742bd7')],
        'at_position_list': [],
        'body': '<p>child comment 1&nbsp;editing</p>',
        'course_id': 'course-v1:Arbisoft+SE002+2024_S2',
        '_type': 'Comment',
        'endorsed': False,
        'anonymous': False,
        'anonymous_to_peers': False,
        'parent_id': ObjectId('66d840c4a3a68c001d742bd7'),
        'author_id': '8',
        'comment_thread_id': ObjectId('66d840b7a3a68c001d742bd5'),
        'child_count': 0,
        'depth': 1,
        'author_username': 'faraz1',
        'sk': '66d840c4a3a68c001d742bd7-66d840cea3a68c001d742bd8',
        'updated_at': datetime.datetime(2024, 9, 4, 11, 13, 45, 441000),
        'created_at': datetime.datetime(2024, 9, 4, 11, 13, 18, 26000),
        'edit_history': [
            {
                '_id': ObjectId('66d840e9a3a68c001d742bdb'),
                'original_body': '<p>child comment 1</p>',
                'reason_code': None,
                'editor_username': 'faraz1',
                'author_id': '8',
                'created_at': datetime.datetime(2024, 9, 4, 11, 13, 45, 441000)
            }
        ]
    }

Relationships
~~~~~~~~~~~~~

* **Thread**: A ``Comment`` belongs to a ``CommentThread``.
* **Parent Comment**: A ``Comment`` can be a child of another ``Comment``.
* **Child Comments**: A ``Comment`` can have multiple child comments.
* **Course**: The ``course_id`` field links to a ``Course`` model.

Users Collection
----------------

The ``users`` collection in MongoDB stores user-related data, including user profiles and related activity within the forum system.

User
^^^^

The ``User`` model represents a user in the system, managing user profiles, subscriptions, and activity.

Fields
~~~~~~

* **_id** (str): Unique identifier for the user.
* **default_sort_key** (str): Default is 'date'.
* **external_id** (str): The ID of the user from edx-platform.
* **username** (str): The username of the user.
* **course_stats** (list[dict]):
    * **_id** (ObjectId): Unique identifier for the course stats record.
    * **active_flags** (int): Number of active flags on comments or threads by the user.
    * **inactive_flags** (int): Number of inactive flags on comments or threads by the user.
    * **threads** (int): Number of threads created by the user.
    * **responses** (int): Number of responses made by the user.
    * **replies** (int): Number of replies made by the user.
    * **course_id** (str): Identifier for the course.
    * **last_activity_at** (datetime): Timestamp of the last activity.

* **read_states** (list[dict]):
    * **_id** (ObjectId): Unique identifier for the read states record.
    * **last_read_times** (dict):
        * **key (str)**: CommentThread ID.
        * **value (datetime)**: Timestamp of the last read time for that thread.
    * **course_id** (str): Identifier for the course.
* **active_flags** (int): Number of active flags on comments or threads by the user.

**Example User Data**:

.. code-block:: python

    {
        '_id': '8',
        'default_sort_key': 'date',
        'external_id': '8',
        'username': 'faraz1',
        'course_stats': [
            {
                '_id': ObjectId('66d6b2f3a3a68c001d742bca'),
                'active_flags': 0,
                'inactive_flags': 0,
                'threads': 2,
                'responses': 0,
                'replies': -1,
                'course_id': 'course-v1:Arbisoft+SE002+2024_S2',
                'last_activity_at': datetime.datetime(2024, 9, 4, 11, 13, 45, 439000)
            }
        ],
        'read_states': [
            {
                '_id': ObjectId('66d6b2f3a3a68c001d742bcb'),
                'last_read_times': {
                    '66d6b2f3a3a68c001d742bc9': datetime.datetime(2024, 9, 3, 6, 55, 47, 425000),
                    '66d6b4ada3a68c001d742bcd': datetime.datetime(2024, 9, 3, 7, 3, 9, 468000),
                    '66d840b7a3a68c001d742bd5': datetime.datetime(2024, 9, 4, 11, 13, 18, 61000)
                },
                'course_id': 'course-v1:Arbisoft+SE002+2024_S2'
            }
        ],
        'active_flags': 1
    }

Relationships
~~~~~~~~~~~~~

* **Comment**: Each ``User`` can author multiple ``Comment`` documents. The ``User`` is linked to ``Comment`` documents through the ``author_id`` field in the ``Comment`` model, allowing the retrieval of comments authored by a specific user.
* **CommentThread**: A ``User`` can be associated with multiple ``CommentThread`` documents through their activities or subscriptions. The ``User`` can influence or participate in multiple threads.
* **Subscription**: Each ``User`` may have multiple ``subscriptions`` to various ``CommentThread`` documents, tracked by the ``Subscription`` model. This relationship allows managing and querying user subscriptions to threads.

Subscriptions Collection
-------------------------

The ``subscriptions`` collection in MongoDB stores data about subscriptions related to content within the forum system.

Subscription
^^^^^^^^^^^^

The ``Subscription`` model represents a subscription to a particular thread or comment, managing user engagement.

Fields
~~~~~~

* **_id** (ObjectId): Unique identifier for the subscription.
* **subscriber_id** (str): The ID of the user who is subscribed.
* **source_id** (str): The ID of the comment thread that the user is subscribed to.
* **source_type** (str): Type of the source, which is default to ``CommentThread``.
* **updated_at** (datetime): Timestamp when the subscription was last updated.
* **created_at** (datetime): Timestamp when the subscription was created.

**Example Subscription Data**:

.. code-block:: python

    {
        '_id': ObjectId('66d840b7a3a68c001d742bd6'),
        'subscriber_id': '8',
        'source_id': '66d840b7a3a68c001d742bd5',
        'source_type': 'CommentThread',
        'updated_at': datetime.datetime(2024, 9, 4, 11, 12, 55, 886000),
        'created_at': datetime.datetime(2024, 9, 4, 11, 12, 55, 886000)
    }

Relationships
~~~~~~~~~~~~~

* **User**: Each ``Subscription`` is associated with a ``User``, representing the user who has subscribed to a thread or comment. This relationship allows querying and managing user subscriptions.
* **CommentThread**: Each ``Subscription`` can be linked to a ``CommentThread``, indicating the thread to which the user has subscribed. This relationship helps in tracking and managing thread subscriptions.

Relationships Overview
-----------------------

Contents to Users
^^^^^^^^^^^^^^^^^

* **CommentThread**: Linked to ``User`` via ``author_id``.
* **Comment**: Linked to ``User`` via ``author_id``.
* **EditHistory**: Linked to ``User`` via ``author_id``.

Users to Subscriptions
^^^^^^^^^^^^^^^^^^^^^^

* **User**: Linked to ``Subscription`` via ``user_id``.

Contents to Subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^

* **CommentThread**: Linked to ``Subscription`` via ``content_id``.
* **Comment**: Linked to ``Subscription`` via ``content_id``.

Conclusion
----------

This documentation provides a detailed overview of the MongoDB collections used in the forum system, highlighting the structure, relationships, and examples of data within the ``contents``, ``users``, and ``subscriptions`` collections. Each model is defined with its fields, relationships, and example data to guide developers and maintainers in understanding and working with the forum data structure.
