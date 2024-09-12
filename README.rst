Open edX Forum
##############

|ci-badge| |license-badge| |status-badge|

⚠️ **THIS IS A WORK IN PROGRESS THAT IS NOT READY FOR PRODUCTION YET** The migration from cs_comments_service is not complete. In particular, the migration from Mongodb to MySQL has not been done yet. But this app should already be working as a drop-in replacement for the legacy cs_comments_service application. If it does not work for you, please open an issue in this repository.

This application provides a forum backend for use within `Open edX <https://openedx.org>`__ courses. Features include: nested comments, voting, instructor endorsements, and others. The frontend is provided by the `frontend-app-discussions <https://github.com/openedx/frontend-app-discussions>`__ microfrontend application.

This project is a drop-in replacement of the legaxy `cs_comments_service <https://github.com/openedx/cs_comments_service>`__ application. The legacy application was written in Ruby, while this one is written in Python for direct integration in the edx-platform Django project. Moreover, forum data no longer resides in MongoDB, but in the relational MySQL database. The motivation for this rewrite is described more extensively in the `Axim Funded Contribution Proposal <https://discuss.openedx.org/t/axim-funded-contribution-proposal-forum-rewrite-from-ruby-mongodb-to-python-mysql/12788>`_.

Installation
************

The only prerequisite is a working Open edX platform with `Tutor <https://docs.tutor.edly.io/>`__, on the `nightly branch <https://docs.tutor.edly.io/tutorials/nightly.html>`__. Make sure to disable the legacy forum plugin::

    tutor plugins disable forum

Install the forum application by running::

    tutor config save --append 'OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edly-io/forum.git@master'
    tutor images build openedx
    tutor local launch

The forum feature will then be automatically enabled in the Open edX platform, and all API calls will be transparently handled by the new application.

Development
***********

When developing this application, it is recommended to clone this repository locally. First, install our custom plugin to auto-mount the forum repository::

    tutor plugins install https://gist.githubusercontent.com/taimoor-ahmed-1/9e947a06d127498a328475877e41d7c0/raw/forumv2.py
    tutor config save
    tutor images build openedx-dev
    tutor dev launch

Then, clone the forum repository and mount it within the application containers::

    git clone git@github.com:edly-io/forum.git
    tutor mounts add ./forum/

Check that the forum repository is properly bind-mounted both at build- and run-time by running ``tutor mounts list``. It should output the following::

    - name: /home/data/regis/projets/overhang/repos/edx/forum
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

Optionally, you may checkout the `edly-io/forum_v2 <https://github.com/edly-io/edx-platform/tree/forum_v2>`__ branch of edx-platform branch that includes custom features, such as troubleshooting differences between the new and the legacy applications::

    cd edx-platform/
    git remote add edly https://github.com/edly-io/edx-platform/
    git fetch edly
    git checkout forum_v2
    tutor mounts add .

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

For anything non-trivial, the best path is to open an issue `in this repository <https://github.com/edly-io/forum/issues>`__ with as many details about the issue you are facing as you can provide.

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

.. |ci-badge| image:: https://github.com/edly-io/forum/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/edly-io/forum/actions/workflows/ci.yml
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/edly-io/forum.svg
    :target: https://github.com/edly-io/forum/blob/master/LICENSE.txt
    :alt: License

.. TODO: Switch to the stable badge once we are ready for production.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
