#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = open("requirements.txt").readlines()

test_requirements = open("requirements_dev.txt").readlines()

setup(
    author="Itay Azolay",
    author_email='itayazolay@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Advanced async proxy utilities for python async framework",
    entry_points={
        'console_scripts': [
            'proxy_plus=proxy_plus.__main__:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='proxy_plus',
    name='proxy_plus',
    packages=find_packages(include=['proxy_plus']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/itayazolay/proxy_plus',
    version='0.1.0',
    zip_safe=False,
)
