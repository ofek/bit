Contributing
============

Filing an Issue
---------------

This is the way to report :ref:`non-security related <vulnerabilities>` issues
and also to request features.

1. Go to `Bit's GitHub Issues <https://github.com/ofek/bit/issues>`_.
2. Look through open and closed issues to see if there has already been a
   similar bug report or feature request.
   `GitHub's search <https://github.com/ofek/bit/search>`_ feature may aid
   you as well.
3. If your issue doesn't appear to be a duplicate,
   `file an issue <https://github.com/ofek/bit/issues/new>`_.
4. Please be as descriptive as possible!

Pull Request
------------

1. Fork the repository `on GitHub <https://github.com/ofek/bit>`_.
2. Create a new branch for your work.
3. Make your changes (see below).
4. If this is your first contribution, add yourself to
   `AUTHORS.rst <https://github.com/ofek/bit/blob/master/AUTHORS.rst>`_.
5. Send a GitHub Pull Request to the ``master`` branch of ``ofek/bit``.

Step 3 is different depending on if you are contributing to the code base or
documentation.

Code
^^^^

1. Install ``pytest`` and ``coverage`` if you don't have them already.
2. Run `run_tests.py <https://github.com/ofek/bit/blob/master/run_tests.py>`_
   which is located in the project directory. If any tests fail, and you
   are unable to diagnose the reason, please refer to `Filing an Issue`_.
3. Complete your patch and write tests to verify your fix or feature is working.
   Please try to reduce the size and scope of your patch to make the review
   process go smoothly.
4. Run the tests again and make any necessary changes to ensure all tests pass.
5. Add any changes to the **Unreleased** section of
   `HISTORY.rst <https://github.com/ofek/bit/blob/master/HISTORY.rst>`_.

Documentation
^^^^^^^^^^^^^

1. Enter the `docs <https://github.com/ofek/bit/tree/master/docs>`_ directory.
2. Make your changes to any files in ``source/``.
3. Run ``make clean && make html``. This will generate html files in a new
   ``build/html/`` directory.
4. Open the generated pages and make any necessary changes to the ``.rst``
   files until the documentation looks properly formatted.

TODO
----

.. include:: ../../../TODO.rst
