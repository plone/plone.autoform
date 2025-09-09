from plone.autoform.testing import optionflags
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import unittest


test_files = [
    "../autoform.rst",
    "subform.txt",
    "../view.txt",
    "../supermodel.txt",
]


def test_suite():
    tests = [
        layered(
            doctest.DocFileSuite(
                test_file,
                optionflags=optionflags,
            ),
            layer=UNIT_TESTING,
        )
        for test_file in test_files
    ]

    return unittest.TestSuite(tests)
