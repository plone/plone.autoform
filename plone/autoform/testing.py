from plone.testing import zca
from plone.testing import zope

import doctest
import plone.autoform


AUTOFORM_FIXTURE = zca.ZCMLSandbox(
    bases=(zope.STARTUP,),
    filename="configure.zcml",
    package=plone.autoform,
    name="plone.autoform:Fixture",
)

AUTOFORM_INTEGRATION_TESTING = zope.IntegrationTesting(
    bases=(AUTOFORM_FIXTURE,), name="plone.autoform:Integration"
)

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
