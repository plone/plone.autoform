import unittest
import doctest

import zope.app.testing.placelesssetup


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../autoform.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        doctest.DocFileSuite('../subform.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        doctest.DocFileSuite('../view.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        doctest.DocFileSuite('../supermodel.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        ))
