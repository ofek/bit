Development
===========

Oversight
---------

`Ofek Lev <https://github.com/ofek>`_, who is also the only current maintainer,
has the final say regarding any new features or API changes.

Philosophy
----------

- Complex workflows can always be enabled through simple APIs
- With planning, simple APIs can always be constructed using clear and concise
  code
- Satisfy the general use cases, then specialize

Continuous Integration
----------------------

`Travis CI`_ is used for testing and `Codecov`_ is used for detailing code
coverage. No pull request will be merged without passing the test suite and
achieving 100% code coverage.

Documentation
-------------

Docs are hosted by `GitHub Pages`_ and are automatically built and published
by Travis after every successful commit to Bit's ``master`` branch.

Version Scheme
--------------

Bit tries to adhere to `semantic versioning`_ as much as possible.

.. _Travis CI: https://travis-ci.org
.. _Codecov: https://codecov.io
.. _GitHub Pages: https://pages.github.com
.. _semantic versioning: https://goo.gl/iQwd4o
