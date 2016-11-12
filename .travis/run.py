import os
import subprocess

version = os.environ.get('TRAVIS_PYTHON_VERSION')
if version and version.startswith('pypy3.3-5.2-'):
    subprocess.call(['pip', 'install', '-U', 'virtualenv'])

subprocess.call(['source', '~/.venv/bin/activate'], shell=True)
subprocess.call(['tox', '--', '-rs'])
