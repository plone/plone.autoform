import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '1.1'

long_description = (
    read('README.txt')
    + '\n' +
    read('plone', 'autoform', 'autoform.txt')
    + '\n' +
    read('plone', 'autoform', 'view.txt')
    + '\n' +
    read('plone', 'autoform', 'supermodel.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='plone.autoform',
      version=version,
      description="Tools to construct z3c.form forms",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone form z3c.form',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://code.google.com/p/dexterity',
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
          'plone.supermodel>=1.0b2',
          'plone.z3cform',
          'z3c.form',
          # 'AccessControl',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
