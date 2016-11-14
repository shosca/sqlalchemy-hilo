#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import os

from setuptools import find_packages, setup

from hilogenerator import __description__, __version__


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'rb') as fid:
        return fid.read().decode('utf-8')


readme = read('README.rst')

requirements = read('requirements.txt').splitlines() + [
    'setuptools',
]


setup(
    name='sqlalchemy-hilo',
    version=__version__,
    description=__description__,
    long_description=readme,
    url='https://github.com/shosca/sqlalchemy-hilo',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=requirements,
    license='MIT',
    keywords=' '.join([
        'generator',
        'hilo',
        'sql',
        'sqlalchemy',
    ]),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Development Status :: 2 - Pre-Alpha',
    ],
)
