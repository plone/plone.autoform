from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "2.0.3"

long_description = (
    f"{Path('README.rst').read_text()}\n" f"{Path('CHANGES.rst').read_text()}"
)

setup(
    name="plone.autoform",
    version=version,
    description="Tools to construct z3c.form forms",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: Core",
        "Framework :: Plone :: 6.0",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone form z3c.form",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="http://github.com/plone/plone.autoform",
    license="LGPL",
    packages=find_packages(),
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "lxml",
        "setuptools",
        "plone.supermodel>=1.3",
        "plone.z3cform>=2.0.0",
        "z3c.form",
        "Zope",
    ],
    extras_require={
        "test": [
            "plone.testing",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
