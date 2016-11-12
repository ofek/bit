import os
import subprocess

version = os.environ.get('TRAVIS_PYTHON_VERSION')
if version and version.startswith('pypy3.3-5.2-'):
    os.environ.pop('pypy3')

subprocess.call(['tox', '--', '-rs'])
