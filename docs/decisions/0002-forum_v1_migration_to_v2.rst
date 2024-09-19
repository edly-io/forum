========================
Forum v1 to v2 Migration
========================

Overview
========

This document outlines the migration process from Forum v1 (written in Ruby) to Forum v2 (rewritten in Python). The migration aimed to optimize the forum's backend and remove unused or redundant components to better suit the current needs of the discussion platform. Below are key decisions made during the migration, focusing on the exclusion of certain models and APIs that were no longer relevant to the new system.

Migration Decisions
===================

Notifications Model
^^^^^^^^^^^^^^^^^^^

*  The ``Notifications`` model is not migrated from Ruby to Python.
* **Reason**: The ``Notifications`` model was not being utilized in the frontend of the current discussion forum.

Notifications API
^^^^^^^^^^^^^^^^^

*  The ``Notifications`` API is not migrated from Ruby to Python.
*  **Endpoints not migrated**:

   .. code-block:: python

      /notifications

*  **Reason**: The ``Notifications`` API was not used by the frontend in the current discussion forum.

Activity Model
^^^^^^^^^^^^^^

*  The ``Activity`` model is not migrated from Ruby to Python.
* **Reason**: Similar to notifications, the ``Activity`` model was also found to be obsolete in the frontend.

Commentable APIs
^^^^^^^^^^^^^^^^

*  The following ``Commentable`` APIs are not migrated from Ruby to Python:

   .. code-block:: python

      /:commentable_id/threads DELETE
      /:commentable_id/threads GET
      /:commentable_id/threads POST

* **Reason**: The ``Commentable`` APIs were found to be unused in the frontend, and the existing structure for handling threads and comments was deemed sufficient.

filter_blocked_content Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*  The ``filter_blocked_content`` method is not migrated from Ruby to Python. This method was being used in ``threads`` and ``comments`` APIs.
* **Functionality**: This method was used in the ``threads`` and ``comments`` APIs to filter the content of a thread or comment by checking against a set of ``blocked_hashes`` stored in MongoDB. If the content matched a blocked hash, the API would return a 503 error.
* **Reason**: There was no mechanism in place in the current discussion forum to add or maintain these blocked hashes. As a result, the method became irrelevant and was not included in the new system.

Improvement in elasticsearch indexes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Issues in V1**:
    - In the initial implementation (v1), the entire dataset from MongoDB was imported directly into Elasticsearch.
    - This led to larger document sizes in Elasticsearch, many of which contained unnecessary fields that did not align with the pre-defined mappings in Elasticsearch.
    - As a result, performance was negatively impacted, with higher storage costs and slower query responses.

* **Optimization in v2**:
   - In version 2, significant improvements were made to enhance the indexing process:
      - Only the fields defined in Elasticsearch mappings were migrated from MongoDB.
      - This reduced the size of each document, improving performance and reducing storage overhead.
      - The optimized mappings streamlined query performance and index management.

* **Example of Indices in v1**:

  .. code-block:: json

   {
     "_index" : "comment_threads_20240904150622420",
     "_type" : "_doc",
     "_id" : "66d8776f8c6533121e36067b",
     "_score" : 1.0,
     "_source" : {
       "abuse_flaggers" : [],
       "anonymous" : false,
       "anonymous_to_peers" : false,
       "at_position_list" : [],
       "author_id" : "cordell.mueller_5",
       "author_username" : "cordell.mueller_5",
       "body" : "a thread about green artichokes",
       "close_reason_code" : null,
       "closed" : false,
       "closed_by_id" : null,
       "comment_count" : 0,
       "commentable_id" : "test_commentable",
       "context" : "course",
       "course_id" : "test/course/id",
       "created_at" : "2024-09-04T15:06:23Z",
       "group_id" : null,
       "historical_abuse_flaggers" : [],
       "last_activity_at" : "2024-09-04T15:06:23Z",
       "pinned" : null,
       "retired_username" : null,
       "thread_type" : "discussion",
       "title" : "a thread about green artichokes",
       "updated_at" : "2024-09-04T15:06:23Z",
       "visible" : true,
       "votes" : {
         "up" : [],
         "down" : [],
         "up_count" : 0,
         "down_count" : 0,
         "count" : 0,
         "point" : 0
       }
     }
   }

  .. code-block:: json

   {
     "_index" : "comments_20240904150622420",
     "_type" : "_doc",
     "_id" : "66d8776f8c6533121e36067d",
     "_score" : 1.0,
     "_source" : {
       "abuse_flaggers" : [],
       "anonymous" : false,
       "anonymous_to_peers" : false,
       "at_position_list" : [],
       "author_id" : "cordell.mueller_5",
       "author_username" : "cordell.mueller_5",
       "body" : "a comment about greed pineapples",
       "child_count" : null,
       "comment_thread_id" : "66d8776f8c6533121e36067b",
       "commentable_id" : "test_commentable",
       "course_id" : "test/course/id",
       "created_at" : "2024-09-04T15:06:23Z",
       "depth" : 0,
       "endorsed" : false,
       "endorsement" : null,
       "historical_abuse_flaggers" : [],
       "parent_id" : null,
       "parent_ids" : [],
       "retired_username" : null,
       "sk" : "66d8776f8c6533121e36067d",
       "updated_at" : "2024-09-04T15:06:23Z",
       "visible" : true,
       "votes" : {
         "up" : [],
         "down" : [],
         "up_count" : 0,
         "down_count" : 0,
         "count" : 0,
         "point" : 0
       }
     }
   }

* **Example of Optimized Indices in v2**:

  .. code-block:: json

   {
     "_index" : "comment_threads_20240904095228",
     "_type" : "_doc",
     "_id" : "66d8742decb2a86851511014",
     "_score" : 1.0,
     "_source" : {
       "id" : "66d8742decb2a86851511014",
       "title" : "a thread about green artichokes",
       "body" : "text",
       "created_at" : "2024-09-04T09:52:29.049000",
       "updated_at" : "2024-09-04T09:52:29.049000",
       "last_activity_at" : "2024-09-04T09:52:29.049000",
       "comment_count" : 0,
       "votes_point" : 0,
       "context" : "course",
       "course_id" : "course_id",
       "commentable_id" : "test_commentable",
       "author_id" : "1",
       "group_id" : null,
       "thread_id" : "66d8742decb2a86851511014"
     }
   }

  .. code-block:: json

   {
     "_index" : "comments_20240904095228",
     "_type" : "_doc",
     "_id" : "66d8742decb2a86851511015",
     "_score" : 1.0,
     "_source" : {
       "body" : "a comment about greed pineapples",
       "course_id" : "course_id",
       "comment_thread_id" : "66d8742decb2a86851511014",
       "commentable_id" : null,
       "group_id" : null,
       "context" : "course",
       "created_at" : "2024-09-04T09:52:29.067000",
       "updated_at" : "2024-09-04T09:52:29.068000",
       "title" : null
     }
   }


Conclusion
==========

The migration of Forum v1 to v2 was guided by a series of strategic decisions aimed at reducing complexity,
removing unused features, and aligning with the current usage of the discussion forum. By streamlining
redundant models and APIs, and transitioning to a more efficient database, the new system is not only
more performant but also better equipped to meet the forum's evolving demands. In parallel, we successfully
migrated the search tests from Ruby to Python, with passing tests confirming that the index changes had no
adverse effects on functionality. Manual verification of the platform further demonstrated that it operates
as expected, reinforcing the reliability of these changes. Together, these efforts ensure a more scalable
and efficient forum system that is optimized for both present and future needs.
