# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '1.7.0'

long_description = (read('README.rst') + '\n' + read('CHANGES.rst'))

setup(
    name='plone.autoform',
    version=version,
    description="Tools to construct z3c.form forms",
    long_description=long_description,
    # Get more strings from https://pypi.python.org/pypi?%3Aaction=list_
    # classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        'Programming Language :: Python :: 2.6',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone form z3c.form',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='http://github.com/plone/plone.autoform',
    license='LGPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.interface',
        'zope.schema',
        'zope.security',
        'zope.dottedname',
        'plone.supermodel>=1.3.dev0',
        'plone.z3cform>=0.9.0.dev0',
        'z3c.form',
        # 'AccessControl',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
