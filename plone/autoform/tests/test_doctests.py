# -*- coding: utf-8 -*-
from plone.autoform.testing import optionflags
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import re
import six
import unittest


test_files = [
    '../autoform.rst',
    'subform.txt',
    '../view.txt',
    '../supermodel.txt',
]


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub("u'(.*?)'", "'\\1'", want)
            # want = re.sub("b'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    tests = [
        layered(
            doctest.DocFileSuite(
                test_file,
                optionflags=optionflags,
                checker=Py23DocChecker(),
            ),
            layer=UNIT_TESTING,
        )
        for test_file in test_files
    ]

    return unittest.TestSuite(tests)
