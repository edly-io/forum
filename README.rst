forum
#############################

|ci-badge| |license-badge|

Purpose
*******

openedx forum app

The Edly Forum app is designed to replace the `CS Comments Service <https://github.com/openedx/cs_comments_service>`_, providing a more robust and flexible forum solution for Open edX instances. This new forum is built in Python and uses MySQL, which enhances performance and maintainability compared to the previous Ruby and MongoDB implementation. The motivation for this rewrite stems from a need for a more streamlined and integrated discussion platform within Open edX, as outlined in the `Axim Funded Contribution Proposal <https://discuss.openedx.org/t/axim-funded-contribution-proposal-forum-rewrite-from-ruby-mongodb-to-python-mysql/12788>`_.

Getting Started with Development
********************************

Prerequisites
==============================================


Before you begin, ensure you have the following installed:

- A working Open edX instance using the Tutor platform.

Installation Steps
==============================================


Follow the steps below to install the Forum app in your Tutor environment:

1. Add a Forum App to the openedX Dependencies
----------------------------------------------

To add this package to the Open edX dependencies, include it in the `OPENEDX_EXTRA_PIP_REQUIREMENTS`. Since the package is not yet available on PyPI, we will install it directly from the Git repository.

Run the following command to append the package to your Tutor configuration::

    tutor config save --append 'OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edly-io/forum.git@master'

2. Save Config and Rebuild open-edX Image
-----------------------------------------

Run the following commands to save the configuration and rebuild the Open edX image::

    tutor config save
    tutor images build openedx

3. Run Launch
-------------

Run the launch command. It is necessary for building the migrations present in the Forum app::

    tutor dev launch

4. Accessing the Forum
----------------------

There are no changes needed in the `Discussion MFE <https://github.com/openedx/frontend-app-discussions>`_. You should see the forum interface where users can start discussions, post comments, and interact with each other. In the backend, the API calls are made via the Forum app instead of the CS Comments Service.

5. Development (For Developers)
-------------------------------

In certain scenarios, you may need to mount the Forum package for extending or debugging features. For this, you need to install the `forumv2 <https://gist.github.com/taimoor-ahmed-1/9e947a06d127498a328475877e41d7c0>`_ plugin. Follow these steps to accomplish this:

1. Mount the edx-platfrom:

    Mount the edx-patfrom using `forum_v2 <https://github.com/edly-io/edx-platform/tree/forum_v2>`_ branch.
    The branch contains updates for better logging to test the Forum V2 APIs

2. Clone the forum repo::

    git clone git@github.com:edly-io/forum.git

3. Mount the repo::

    tutor mounts add path/to/forum/repo

4. Install this plugin::

    tutor plugins install https://gist.githubusercontent.com/taimoor-ahmed-1/9e947a06d127498a328475877e41d7c0/raw/6152bdc312f941e79d50e2043f00d3d059de70a7/forum-v2.py

5. Enable the plugin::

    tutor plugins enable forumv2

6. Save Changes::

    tutor config save

7. Build the openedx-dev Docker image::

    tutor images build openedx-dev

8. Launch the platform::

    tutor dev launch

Deploying
*********

TODO: How can a new user go about deploying this component? Is it just a few
commands? Is there a larger how-to that should be linked here?

PLACEHOLDER: For details on how to deploy this component, see the `deployment how-to`_.

.. _deployment how-to: https://docs.openedx.org/projects/forum/how-tos/how-to-deploy-this-component.html

Getting Help
************

Documentation
=============

PLACEHOLDER: Start by going through `the documentation`_.  If you need more help see below.

.. _the documentation: https://docs.openedx.org/projects/forum

(TODO: `Set up documentation <https://openedx.atlassian.net/wiki/spaces/DOC/pages/21627535/Publish+Documentation+on+Read+the+Docs>`_)

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/openedx/forum/issues

For more information about these options, see the `Getting Help <https://openedx.org/getting-help>`__ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to discuss your new feature idea with the maintainers before beginning development
to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/forum

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |ci-badge| image:: https://github.com/edly-io/forum/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/edly-io/forum/actions
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/openedx/forum.svg
    :target: https://github.com/edly-io/forum/blob/master/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
