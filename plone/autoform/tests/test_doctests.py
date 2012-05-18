import unittest
import doctest

import zope.component.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../autoform.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        doctest.DocFileSuite('../subform.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        doctest.DocFileSuite('../view.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        doctest.DocFileSuite('../supermodel.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        ))
