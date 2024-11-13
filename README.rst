Open edX Forum
##############

|ci-badge| |license-badge| |status-badge|

This application provides a forum backend for use within `Open edX <https://openedx.org>`__ courses. Features include: nested comments, voting, instructor endorsements, and others. The frontend is provided by the `frontend-app-discussions <https://github.com/openedx/frontend-app-discussions>`__ microfrontend application.

This project is a drop-in replacement of the legacy `cs_comments_service <https://github.com/openedx/cs_comments_service>`__ application. The legacy application was written in Ruby, while this one is written in Python for direct integration in the edx-platform Django project. Moreover, forum data no longer resides in MongoDB, but in the relational MySQL database. The motivation for this rewrite is described more extensively in the `Axim Funded Contribution Proposal <https://discuss.openedx.org/t/axim-funded-contribution-proposal-forum-rewrite-from-ruby-mongodb-to-python-mysql/12788>`_.

Installation
************

⚠️ At the moment, the forum is not yet fully integrated in Tutor. Users will need to install the forum plugin from the `regisb/forumv2 <https://github.com/overhangio/tutor-forum/pull/48>`__ branch.

The only prerequisite is a working Open edX platform with `Tutor <https://docs.tutor.edly.io/>`__, on the Sumac release (v19+) or the `nightly branch <https://docs.tutor.edly.io/tutorials/nightly.html>`__. Enable the forum by running::

    tutor plugins enable forum
    tutor local launch

The forum feature will then be automatically enabled in the Open edX platform, and all API calls will be transparently handled by the new application.

Development
***********

Run tests with::

    make test-all       # run all tests
    make test           # run unit tests only
    make test-quality   # run quality tests only
    make test-e2e       # run end-to-end tests only

When developing this application, it is recommended to clone this repository locally and mount it within the application containers::

    git clone git@github.com:openedx/forum.git
    tutor mounts add ./forum/

Check that the forum repository is properly bind-mounted both at build- and run-time by running ``tutor mounts list``. It should output the following::

    - name: /home/path/to/forum
      build_mounts:
      - image: openedx
        context: mnt-forum
      - image: openedx-dev
        context: mnt-forum
      compose_mounts:
      - service: openedx
        container_path: /mnt/forum
      - service: openedx-dev
        container_path: /mnt/forum

Re-build the openedx-dev image and launch the platform::

    tutor images build openedx-dev
    tutor dev launch

Administration
**************

Deployment of the forum v2 application is gated by two course waffle flags. In addition, this application provides a few commands to facilitate the transition from the legacy forum app.

Forum v2 toggle
---------------

In edx-platform, forum v2 is not enabled by default and edx-platform will keep communicating with the legacy forum app. To enable forum v2 in your Open edX platform, toggle the ``discussions.enable_forum_v2`` course waffle flag::

    ./manage.py lms waffle_flag --create --everyone discussions.enable_forum_v2

Note that Tutor enables this flag for all forum plugin users, such that you don't have to run this command yourself. If you wish to migrate your courses one by one to the new forum v2 app, you may create the corresponding "Waffle flag course override" objects in your LMS administration panel, at: ``http(s)://<LMS_HOST>/admin/waffle_utils/waffleflagcourseoverridemodel/``.

MySQL backend toggle
--------------------

To preserve the legacy behaviour of storing data in MongoDB, the forum v2 app makes it possible to keep using MongoDB as a data backend. However, it is strongly recommended to switch to the MySQL storage backend by toggling the ``forum_v2.enable_mysql_backend`` course waffle flag::

    ./manage.py lms waffle_flag --create --everyone forum_v2.enable_mysql_backend

Here again, Tutor creates this flag by default, such that you don't have to create it yourself. If you decide to switch to MySQL, you will have to migrate your data from MongoDB -- see instructions below.

Migration from MongoDB to MySQL
-------------------------------

The forum v2 app comes with the ``forum_migrate_courses_to_mysql`` migration command to move data from MongoDB to MySQL. This command will perform the following steps:

1. Migrate data: user, content and read state data from MongoDB to MySQL.
2. Enable the ``forum_v2.enable_mysql_backend`` waffle flag for the specified course(s).

To migrate data for specific courses, run the command with the course IDs as argument::

   ./manage.py lms forum_migrate_course_from_mongodb_to_mysql <course_id_1> <course_id_2>

To migrate data for all courses, run the command with the ``all`` argument::

   ./manage.py lms forum_migrate_course_from_mongodb_to_mysql all

To test data migration without actually creating course toggles, use the ``--no-toggle`` option::

    ./manage.py lms forum_migrate_course_from_mongodb_to_mysql --no-toggle all

⚠️ Note that the command will create toggles only for the processed courses. Courses created in the future will not automatically use the MySQL backend unless you create the global waffle flag with the ``waffle_flag --create`` command indicated above.

MongoDB data deletion
---------------------

After you have successfully migrated your course data from MySQL to MongoDB using the command above, you may delete your MongoDB data using the ``forum_delete_course_from_mongodb`` management command. This command deletes course data from MongoDB for the specified courses.

Run the command with the course ID(s) as an argument::

   ./manage.py lms forum_delete_course_from_mongodb <course_id_1> <course_id_2>

To delete data for all courses, run the command with the ``all`` argument::

   ./manage.py lms forum_delete_course_from_mongodb all

To try out changes before applying them, use the ``--dry-run`` option. For instance::

   ./manage.py lms forum_delete_course_from_mongodb all --dry-run

.. Deploying
.. *********

.. TODO: How can a new user go about deploying this component? Is it just a few
.. commands? Is there a larger how-to that should be linked here?

.. PLACEHOLDER: For details on how to deploy this component, see the `deployment how-to`_.

.. .. _deployment how-to: https://docs.openedx.org/projects/forum/how-tos/how-to-deploy-this-component.html

Getting Help
************

.. Documentation
.. =============

.. PLACEHOLDER: Start by going through `the documentation`_.  If you need more help see below.

.. .. _the documentation: https://docs.openedx.org/projects/forum

.. (TODO: `Set up documentation <https://openedx.atlassian.net/wiki/spaces/DOC/pages/21627535/Publish+Documentation+on+Read+the+Docs>`_)

.. More Help
.. =========

If you are having trouble, we have discussion forums at https://discuss.openedx.org where you can connect with others in the community.

Our real-time conversations are on Slack. You can request a `Slack invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue `in this repository <https://github.com/openedx/forum/issues>`__ with as many details about the issue you are facing as you can provide.

For more information about these options, see the `Getting Help <https://openedx.org/getting-help>`__ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/

License
*******

The code in this repository is licensed under the AGPL 3.0 unless otherwise noted. See `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome. Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes, security fixes, maintenance work, or new features. However, please make sure to discuss your new feature idea with the maintainers before beginning development to maximize the chances of your change being accepted. You can start a conversation by creating a new issue on this repo summarizing your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml`` file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/forum

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |ci-badge| image:: https://github.com/openedx/forum/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/openedx/forum/actions/workflows/ci.yml
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/openedx/forum.svg
    :target: https://github.com/openedx/forum/blob/master/LICENSE.txt
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
