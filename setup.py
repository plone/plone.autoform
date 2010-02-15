from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='plone.autoform',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("plone", "autoform", "autoform.txt")).read() + "\n" +
                       open(os.path.join("plone", "autoform", "view.txt")).read() + "\n" +
                       open(os.path.join("plone", "autoform", "supermodel.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
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
          # 'AccessControl',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
