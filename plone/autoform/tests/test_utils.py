import unittest
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from zope.component import provideUtility
from zope.interface import Interface, Invalid
from z3c.form.form import Form
from z3c.form.validator import SimpleFieldValidator
import zope.schema
import zope.component.testing
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.autoform.utils import processFields

class TestValidator(SimpleFieldValidator):
    
    def validate(self, value):
        super(TestValidator, self).validate(value)
        raise Invalid("Test")


class TestUtils(unittest.TestCase):
    
    def setUp(self):
        from zope.security.permission import Permission
        provideUtility(Permission('foo', u'foo', u''), name=u'foo')
        
        class DummySecurityManager(object):
            checks = []
            def checkPermission(self, perm, context):
                self.checks.append(perm)
                return False
        self.secman = DummySecurityManager()
        setSecurityManager(self.secman)
    
    def tearDown(self):
        noSecurityManager()
        zope.component.testing.tearDown()
    
    def test_processFields_permissionChecks_no_prefix(self):
        form = Form(None, None)
        form.groups = ()
        class schema(Interface):
            title = zope.schema.TextLine()
        schema.setTaggedValue(WRITE_PERMISSIONS_KEY, {'title': 'foo'})
        processFields(form, schema, prefix='', permissionChecks=True)
        
        self.assertEqual('foo', self.secman.checks.pop())
        self.assertFalse('title' in form.fields)

    def test_processFields_permissionChecks_w_prefix(self):
        form = Form(None, None)
        form.groups = ()
        class schema(Interface):
            title = zope.schema.TextLine()
        schema.setTaggedValue(WRITE_PERMISSIONS_KEY, {'title': 'foo'})
        processFields(form, schema, prefix='prefix', permissionChecks=True)
        
        self.assertEqual('foo', self.secman.checks.pop())
        self.assertFalse('prefix.title' in form.fields)
