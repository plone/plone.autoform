# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        layered(
            doctest.DocFileSuite(
                '../autoform.rst',
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,),
            layer=UNIT_TESTING),
        layered(
            doctest.DocFileSuite(
                'subform.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,),
            layer=UNIT_TESTING),
        layered(
            doctest.DocFileSuite(
                '../view.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,),
            layer=UNIT_TESTING),
        layered(
            doctest.DocFileSuite(
                '../supermodel.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,),
            layer=UNIT_TESTING),
    ))
