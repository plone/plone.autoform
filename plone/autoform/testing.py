# -*- coding: utf-8 -*-
from plone.testing import z2
from plone.testing import zca

import plone.autoform


AUTOFORM_FIXTURE = zca.ZCMLSandbox(
    bases=(z2.STARTUP,),
    filename='configure.zcml',
    package=plone.autoform,
    name='plone.autoform:Fixture')

AUTOFORM_INTEGRATION_TESTING = z2.IntegrationTesting(
    bases=(AUTOFORM_FIXTURE,),
    name='plone.autoform:Integration')
