========================
Forum v1 to v2 Migration
========================

Overview
========

During the migration of the Forum v1 from Ruby code to Forum v2 in Python, several decisions were made to streamline the process and ensure the new system is optimized for current usage. The following outlines the key decisions taken:

Migration Decisions
===================

1. Notifications Model
^^^^^^^^^^^^^^^^^^^^^^

*  The ``Notifications`` model is not migrated from Ruby to Python.
*  **Reason**: The model was not being used in the frontend, i.e., in the current discussion forum.

2. Notifications API
^^^^^^^^^^^^^^^^^^^^

*  The ``Notifications`` API is not migrated from Ruby to Python.
*  **Endpoints not migrated**:

   .. code-block:: python

      /notifications

*  **Reason**: The API was not being used in the frontend, i.e. in the current discussion forum.

3. Activity Model
^^^^^^^^^^^^^^^^^

*  The ``Activity`` model is not migrated from Ruby to Python.
*  **Reason**: The model was not being used in the frontend, i.e. in the current discussion forum.

4. Commentable APIs
^^^^^^^^^^^^^^^^^^^

*  The following ``Commentable`` APIs are not migrated from Ruby to Python:

   .. code-block:: python

      /:commentable_id/threads DELETE
      /:commentable_id/threads GET
      /:commentable_id/threads POST

*  **Reason**: These APIs were not being used in the frontend, i.e., in the current discussion forum.

5. filter_blocked_content Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*  The ``filter_blocked_content`` method is not migrated from Ruby to Python. This method was being used in ``threads`` and ``comments`` APIs.
*  **Functionality**: It was filtering the body (content) of the post or comment and returning 503 if the body (content) matched with the blocked_hashes.
*  **Reason**: There's no clue or way of adding blocked hashes in the Forum v1 current implementation, i.e., in the current discussion forum. Thus, the body (content) of a comment or thread could not be matched and blocked.

Conclusion
==========

The decisions made during the migration were guided by the current usage of the discussion forum, focusing on removing unused models and APIs to simplify the system and improve performance.
