from setuptools import find_packages, setup

setup(
    name='bit',
    version='0.1.0',
    description='Bitcoin made easy.',
    long_description=open('README.rst', 'r').read(),
    author='Ofek Lev',
    author_email='ofekmeister@gmail.com',
    maintainer='Ofek Lev',
    maintainer_email='ofekmeister@gmail.com',
    url='https://github.com/ofek/bit',
    download_url='https://github.com/ofek/bit',
    license='MIT',

    keywords=(
        'bitcoin',
        'bitcoin tools',
        'bitcoin wallet',
        'address generator',
    ),

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),

    install_requires=['click', 'cryptography', 'requests'],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bit = bit.cli:bit',
        ],
    },
)
