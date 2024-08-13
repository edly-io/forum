.. _chapter-testing:

Testing
#######

This project has an assortment of test cases and code quality checks to catch potential problems during development. To run them all in the
version of Python you chose for your virtualenv:

.. code-block:: bash

    $ make test-all

To run just the unit tests:

.. code-block:: bash

    $ make test

To run just the unit tests and check the difference in coverage with the master branch:

.. code-block:: bash

    $ diff-cover --compare-branch=master coverage.xml

To run just the code quality checks (including mypy checks):

.. code-block:: bash

    $ make test-quality

To run the unit tests under every supported Python version and the code
quality checks:

.. code-block:: bash

    $ tox -e pii_check,quality,py,docs

To generate and open an HTML report of how much of the code is covered by
test cases:

.. code-block:: bash

    $ make coverage
