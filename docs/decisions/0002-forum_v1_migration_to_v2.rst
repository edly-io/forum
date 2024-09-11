========================
Forum v1 to v2 Migration
========================

Overview
========

This document outlines the migration process from Forum v1 (written in Ruby) to Forum v2 (rewritten in Python). The migration aimed to optimize the forum's backend and remove unused or redundant components to better suit the current needs of the discussion platform. Below are key decisions made during the migration, focusing on the exclusion of certain models and APIs that were no longer relevant to the new system.

Migration Decisions
===================

1. Notifications Model
^^^^^^^^^^^^^^^^^^^^^^

*  The ``Notifications`` model is not migrated from Ruby to Python.
* **Reason**: The ``Notifications`` model was not being utilized in the frontend of the current discussion forum.

2. Notifications API
^^^^^^^^^^^^^^^^^^^^

*  The ``Notifications`` API is not migrated from Ruby to Python.
*  **Endpoints not migrated**:

   .. code-block:: python

      /notifications

*  **Reason**: The ``Notifications`` API was not used by the frontend in the current discussion forum.

3. Activity Model
^^^^^^^^^^^^^^^^^

*  The ``Activity`` model is not migrated from Ruby to Python.
* **Reason**: Similar to notifications, the ``Activity`` model was also found to be obsolete in the frontend.

4. Commentable APIs
^^^^^^^^^^^^^^^^^^^

*  The following ``Commentable`` APIs are not migrated from Ruby to Python:

   .. code-block:: python

      /:commentable_id/threads DELETE
      /:commentable_id/threads GET
      /:commentable_id/threads POST

* **Reason**: The ``Commentable`` APIs were found to be unused in the frontend, and the existing structure for handling threads and comments was deemed sufficient.

5. filter_blocked_content Method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*  The ``filter_blocked_content`` method is not migrated from Ruby to Python. This method was being used in ``threads`` and ``comments`` APIs.
* **Functionality**: This method was used in the ``threads`` and ``comments`` APIs to filter the content of a thread or comment by checking against a set of ``blocked_hashes`` stored in MongoDB. If the content matched a blocked hash, the API would return a 503 error.
* **Reason**: There was no mechanism in place in the current discussion forum to add or maintain these blocked hashes. As a result, the method became irrelevant and was not included in the new system.

Conclusion
==========

The migration of Forum v1 to v2 involved several critical decisions focused on reducing complexity, removing unused features, and aligning with the current usage of the discussion forum. By eliminating redundant models and APIs, and shifting to a more performant database, the new system is streamlined and better suited to handle the forum's current and future needs.
