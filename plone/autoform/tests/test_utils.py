# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.autoform.utils import processFields
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.testing.zca import UNIT_TESTING
from z3c.form.form import Form
from z3c.form.validator import SimpleFieldValidator
from zope.component import provideUtility
from zope.interface import Interface
from zope.interface import Invalid

import unittest
import zope.schema


class TestValidator(SimpleFieldValidator):

    def validate(self, value):
        super(TestValidator, self).validate(value)
        raise Invalid('Test')


class TestUtils(unittest.TestCase):

    layer = UNIT_TESTING

    def setUp(self):
        from zope.security.permission import Permission
        provideUtility(Permission('foo', u'foo', u''), name=u'foo')

        class DummySecurityManager(object):
            checks = []

            def checkPermission(self, perm, context):
                self.checks.append(perm)
                return False

        self.oldsecman = getSecurityManager()
        self.secman = DummySecurityManager()
        setSecurityManager(self.secman)

    def tearDown(self):
        setSecurityManager(self.oldsecman)

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

    def test_processFields_fieldsets_as_form_groups(self):
        form = Form(None, None)
        form.groups = []

        class schema(Interface):
            title = zope.schema.TextLine()

        fieldset = Fieldset('custom', label=u'Custom',
                            fields=['title'])
        schema.setTaggedValue(FIELDSETS_KEY, [fieldset])

        class subschema(schema):
            subtitle = zope.schema.TextLine()

        fieldset = Fieldset('custom', label=u'Custom',
                            fields=['subtitle'])
        subschema.setTaggedValue(FIELDSETS_KEY, [fieldset])

        processFields(form, subschema,
                      prefix='prefix', permissionChecks=True)

        self.assertEqual(len(form.groups), 1)
        self.assertEqual(len(form.groups[0].fields), 2)
        self.assertEqual([g.__name__ for g in form.groups], ['custom'])

    def test_fieldset_configuration(self):
        """Test, if fieldsets can be orderd via fieldset configuration on a
        schema without fields. This schema should also not be included in form
        groups.
        """
        form = Form(None, None)
        form.groups = []

        class schema1(Interface):
            title = zope.schema.TextLine()

        fs1 = Fieldset('fs1', label=u'fs1', fields=['title'])
        schema1.setTaggedValue(FIELDSETS_KEY, [fs1])

        class schema2(Interface):
            subtitle = zope.schema.TextLine()

        fs2 = Fieldset('fs2', label=u'fs2', fields=['subtitle'])
        schema2.setTaggedValue(FIELDSETS_KEY, [fs2])

        class schema3(Interface):
            pass

        fs3 = Fieldset('fs1', order=2)
        fs4 = Fieldset('fs2', order=1)
        schema3.setTaggedValue(FIELDSETS_KEY, [fs3, fs4])

        processFields(form, schema1, prefix='prefix', permissionChecks=True)
        processFields(form, schema2, prefix='prefix', permissionChecks=True)
        processFields(form, schema3, prefix='prefix', permissionChecks=True)

        self.assertEqual(len(form.groups), 2)

        self.assertEqual(form.groups[0].__name__, 'fs1')
        self.assertEqual(form.groups[0].order, 2)

        self.assertEqual(form.groups[1].__name__, 'fs2')
        self.assertEqual(form.groups[1].order, 1)
