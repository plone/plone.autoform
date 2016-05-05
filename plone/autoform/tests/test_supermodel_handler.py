# -*- coding: utf-8 -*-
from lxml import etree
from plone.autoform.interfaces import MODES_KEY
from plone.autoform.interfaces import OMITTED_KEY
from plone.autoform.interfaces import ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.autoform.supermodel import FormSchema
from plone.autoform.supermodel import SecuritySchema
from plone.autoform.testing import AUTOFORM_INTEGRATION_TESTING
from plone.supermodel.utils import ns
from z3c.form.interfaces import IEditForm
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IWidget
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import unittest2 as unittest
import zope.schema


@implementer(IWidget)
class DummyWidget(object):

    def __init__(self, request):
        pass


class TestFormSchema(unittest.TestCase):

    layer = AUTOFORM_INTEGRATION_TESTING

    namespace = 'http://namespaces.plone.org/supermodel/form'

    def test_read(self):
        field_node = etree.Element('field')
        field_node.set(
            ns('widget', self.namespace),
            'z3c.form.browser.password.PasswordFieldWidget'
        )
        field_node.set(ns('mode', self.namespace), 'hidden')
        field_node.set(ns('omitted', self.namespace), 'true')
        field_node.set(ns('before', self.namespace), 'somefield')
        field_node.set(
            ns('validator', self.namespace),
            'plone.autoform.tests.test_utils.TestValidator'
        )

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy')

        handler = FormSchema()
        handler.read(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(
            {'dummy': 'z3c.form.browser.password.PasswordFieldWidget'},
            IDummy.getTaggedValue(WIDGETS_KEY)
        )
        self.assertEqual(
            [(Interface, 'dummy', 'true')],
            IDummy.getTaggedValue(OMITTED_KEY)
        )
        self.assertEqual(
            [(Interface, 'dummy', 'hidden')],
            IDummy.getTaggedValue(MODES_KEY)
        )
        self.assertEqual(
            [('dummy', 'before', 'somefield',)],
            IDummy.getTaggedValue(ORDER_KEY)
        )
        validator = getMultiAdapter(
            (None, None, None, IDummy['dummy'], None),
            IValidator
        )
        from plone.autoform.tests.test_utils import TestValidator
        assert isinstance(validator, TestValidator)

    def test_read_multiple(self):
        field_node1 = etree.Element('field')
        field_node1.set(
            ns('widget', self.namespace),
            'z3c.form.browser.password.PasswordFieldWidget'
        )
        field_node1.set(ns('mode', self.namespace), 'hidden')
        field_node1.set(ns('omitted', self.namespace), 'true')
        field_node1.set(ns('before', self.namespace), 'somefield')

        field_node2 = etree.Element('field')
        field_node2.set(ns('mode', self.namespace), 'display')
        field_node2.set(ns('omitted', self.namespace), 'yes')

        class IDummy(Interface):
            dummy1 = zope.schema.TextLine(title=u'dummy1')
            dummy2 = zope.schema.TextLine(title=u'dummy2')

        handler = FormSchema()
        handler.read(field_node1, IDummy, IDummy['dummy1'])
        handler.read(field_node2, IDummy, IDummy['dummy2'])

        self.assertEqual(
            {'dummy1': 'z3c.form.browser.password.PasswordFieldWidget'},
            IDummy.getTaggedValue(WIDGETS_KEY)
        )
        self.assertEqual(
            [(Interface, 'dummy1', 'true'), (Interface, 'dummy2', 'yes')],
            IDummy.getTaggedValue(OMITTED_KEY)
        )
        self.assertEqual(
            [(Interface, 'dummy1', 'hidden'),
             (Interface, 'dummy2', 'display')],
            IDummy.getTaggedValue(MODES_KEY)
        )
        self.assertEqual(
            [('dummy1', 'before', 'somefield',)],
            IDummy.getTaggedValue(ORDER_KEY)
        )

    def test_read_no_data(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy1')

        handler = FormSchema()
        handler.read(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEqual(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEqual(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEqual(None, IDummy.queryTaggedValue(ORDER_KEY))

    def test_read_values_with_interfaces(self):
        field_node1 = etree.Element('field')
        field_node1.set(
            ns('mode', self.namespace),
            'z3c.form.interfaces.IForm:hidden'
        )
        field_node1.set(
            ns('omitted', self.namespace),
            'z3c.form.interfaces.IForm:true'
        )

        field_node2 = etree.Element('field')
        field_node2.set(
            ns('mode', self.namespace),
            'z3c.form.interfaces.IForm:hidden '
            'z3c.form.interfaces.IEditForm:display'
        )
        field_node2.set(
            ns('omitted', self.namespace),
            'z3c.form.interfaces.IForm:true '
            'z3c.form.interfaces.IEditForm:false'
        )

        class IDummy(Interface):
            dummy1 = zope.schema.TextLine(title=u'dummy1')
            dummy2 = zope.schema.TextLine(title=u'dummy2')

        handler = FormSchema()
        handler.read(field_node1, IDummy, IDummy['dummy1'])
        handler.read(field_node2, IDummy, IDummy['dummy2'])

        expected_modes = [
            (IForm, u'dummy1', 'hidden'),
            (IForm, u'dummy2', 'hidden'),
            (IEditForm, u'dummy2', 'display')
        ]
        self.assertEqual(
            expected_modes,
            IDummy.queryTaggedValue(MODES_KEY)
        )
        expected_omitted = [
            (IForm, u'dummy1', 'true'),
            (IForm, u'dummy2', 'true'),
            (IEditForm, u'dummy2', 'false')
        ]
        self.assertEqual(
            expected_omitted,
            IDummy.queryTaggedValue(OMITTED_KEY)
        )

    def test_read_parameterized_widget(self):
        from plone.autoform.widgets import ParameterizedWidget

        param_node = etree.Element('klass')
        param_node.text = 'custom'
        widget_node = etree.Element(ns('widget', self.namespace))
        widget_node.set(
            'type',
            'plone.autoform.tests.test_supermodel_handler.DummyWidget'
        )
        widget_node.append(param_node)
        field_node = etree.Element('field')
        field_node.append(widget_node)

        class IDummy(Interface):
            foo = zope.schema.TextLine(title=u'foo')

        handler = FormSchema()
        handler.read(field_node, IDummy, IDummy['foo'])

        widgets = IDummy.queryTaggedValue(WIDGETS_KEY)
        self.assertTrue(isinstance(widgets['foo'], ParameterizedWidget))
        self.assertTrue(widgets['foo'].widget_factory is DummyWidget)
        self.assertEqual(widgets['foo'].params, {'klass': 'custom'})

    def test_read_parameterized_widget_default(self):
        from plone.autoform.widgets import ParameterizedWidget

        param_node = etree.Element('klass')
        param_node.text = 'custom'
        widget_node = etree.Element(ns('widget', self.namespace))
        widget_node.append(param_node)
        field_node = etree.Element('field')
        field_node.append(widget_node)

        class IDummy(Interface):
            foo = zope.schema.TextLine(title=u'foo')

        handler = FormSchema()
        handler.read(field_node, IDummy, IDummy['foo'])

        widgets = IDummy.queryTaggedValue(WIDGETS_KEY)
        self.assertTrue(isinstance(widgets['foo'], ParameterizedWidget))
        self.assertTrue(widgets['foo'].widget_factory is None)
        self.assertEqual(widgets['foo'].params, {'klass': 'custom'})

    def test_write(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy1')

        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy': 'SomeWidget'})
        IDummy.setTaggedValue(OMITTED_KEY, [(Interface, 'dummy', 'true')])
        IDummy.setTaggedValue(MODES_KEY, [(Interface, 'dummy', 'hidden')])
        IDummy.setTaggedValue(ORDER_KEY, [('dummy', 'before', 'somefield',)])

        handler = FormSchema()
        handler.write(field_node, IDummy, IDummy['dummy'])

        widget_node = field_node.find(ns('widget', self.namespace))
        self.assertEqual('SomeWidget', widget_node.get('type'))
        self.assertEqual('true', field_node.get(ns('omitted', self.namespace)))
        self.assertEqual('hidden', field_node.get(ns('mode', self.namespace)))
        self.assertEqual(
            'somefield',
            field_node.get(ns('before', self.namespace))
        )

    def test_write_partial(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy1')

        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy': 'SomeWidget'})
        IDummy.setTaggedValue(OMITTED_KEY, [(Interface, 'dummy2', 'true')])
        IDummy.setTaggedValue(
            MODES_KEY,
            [(Interface, 'dummy', 'display'), (Interface, 'dummy2', 'hidden')]
        )
        IDummy.setTaggedValue(ORDER_KEY, [])

        handler = FormSchema()
        handler.write(field_node, IDummy, IDummy['dummy'])

        widget_node = field_node.find(ns('widget', self.namespace))
        self.assertEqual('SomeWidget', widget_node.get('type'))
        self.assertEqual(None, field_node.get(ns('omitted', self.namespace)))
        self.assertEqual('display', field_node.get(ns('mode', self.namespace)))
        self.assertEqual(None, field_node.get(ns('before', self.namespace)))

    def test_write_no_data(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy1')

        handler = FormSchema()
        handler.write(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(None, field_node.find(ns('widget', self.namespace)))
        self.assertEqual(None, field_node.get(ns('omitted', self.namespace)))
        self.assertEqual(None, field_node.get(ns('mode', self.namespace)))
        self.assertEqual(None, field_node.get(ns('before', self.namespace)))

    def test_write_values_with_interfaces(self):
        field_node1 = etree.Element('field')
        field_node2 = etree.Element('field')

        class IDummy(Interface):
            dummy1 = zope.schema.TextLine(title=u'dummy1')
            dummy2 = zope.schema.TextLine(title=u'dummy2')

        modes_values = [
            (IForm, u'dummy1', 'hidden'),
            (IForm, u'dummy2', 'hidden'),
            (IEditForm, u'dummy2', 'display')
        ]
        IDummy.setTaggedValue(MODES_KEY, modes_values)
        omitted_values = [
            (IForm, u'dummy1', 'true'),
            (IForm, u'dummy2', 'true'),
            (IEditForm, u'dummy2', 'false')
        ]
        IDummy.setTaggedValue(OMITTED_KEY, omitted_values)

        handler = FormSchema()
        handler.write(field_node1, IDummy, IDummy['dummy1'])
        handler.write(field_node2, IDummy, IDummy['dummy2'])

        self.assertEqual(
            'z3c.form.interfaces.IForm:hidden',
            field_node1.get(ns('mode', self.namespace))
        )
        self.assertEqual(
            'z3c.form.interfaces.IForm:true',
            field_node1.get(ns('omitted', self.namespace))
        )

        self.assertEqual(
            'z3c.form.interfaces.IForm:hidden '
            'z3c.form.interfaces.IEditForm:display',
            field_node2.get(ns('mode', self.namespace))
        )
        self.assertEqual(
            'z3c.form.interfaces.IForm:true '
            'z3c.form.interfaces.IEditForm:false',
            field_node2.get(ns('omitted', self.namespace))
        )

    def test_write_parameterized_widget_string(self):
        from plone.autoform.widgets import ParameterizedWidget
        pw = ParameterizedWidget('foo')

        class IDummy(Interface):
            dummy1 = zope.schema.Text(title=u'dummy1')
        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy1': pw})

        fieldNode = etree.Element('field')
        handler = FormSchema()
        handler.write(fieldNode, IDummy, IDummy['dummy1'])

        self.assertEqual(
            etree.tostring(fieldNode),
            '<field><ns0:widget'
            ' xmlns:ns0="http://namespaces.plone.org/supermodel/form"'
            ' type="foo"/></field>'
        )

    def test_write_parameterized_widget_default(self):
        from plone.autoform.widgets import ParameterizedWidget
        pw = ParameterizedWidget(None)

        class IDummy(Interface):
            dummy1 = zope.schema.Text(title=u'dummy1')
        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy1': pw})

        fieldNode = etree.Element('field')
        handler = FormSchema()
        handler.write(fieldNode, IDummy, IDummy['dummy1'])

        self.assertEqual(
            etree.tostring(fieldNode),
            '<field/>'
        )

    def test_write_parameterized_widget_with_handler(self):
        from plone.autoform.widgets import ParameterizedWidget
        pw = ParameterizedWidget(DummyWidget, klass='custom')

        class IDummy(Interface):
            dummy1 = zope.schema.Text(title=u'dummy1')
        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy1': pw})

        fieldNode = etree.Element('field')
        handler = FormSchema()
        handler.write(fieldNode, IDummy, IDummy['dummy1'])

        self.assertEqual(
            etree.tostring(fieldNode),
            '<field><ns0:widget'
            ' xmlns:ns0="http://namespaces.plone.org/supermodel/form"'
            ' type="plone.autoform.tests.test_supermodel_handler.'
            'DummyWidget">'
            '<klass>custom</klass>'
            '</ns0:widget></field>')

    def test_write_parameterized_widget_default_with_handler(self):
        from plone.autoform.widgets import ParameterizedWidget
        pw = ParameterizedWidget(None, klass='custom')

        class IDummy(Interface):
            dummy1 = zope.schema.Text(title=u'dummy1')
        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy1': pw})

        fieldNode = etree.Element('field')
        handler = FormSchema()
        handler.write(fieldNode, IDummy, IDummy['dummy1'])

        self.assertEqual(
            etree.tostring(fieldNode),
            '<field><ns0:widget'
            ' xmlns:ns0="http://namespaces.plone.org/supermodel/form">'
            '<klass>custom</klass></ns0:widget></field>')


class TestSecuritySchema(unittest.TestCase):

    namespace = 'http://namespaces.plone.org/supermodel/security'

    def test_read(self):
        field_node = etree.Element('field')
        field_node.set(ns('read-permission', self.namespace), 'dummy.Read')
        field_node.set(ns('write-permission', self.namespace), 'dummy.Write')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy')

        handler = SecuritySchema()
        handler.read(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(
            {u'dummy': 'dummy.Read'},
            IDummy.getTaggedValue(READ_PERMISSIONS_KEY)
        )
        self.assertEqual(
            {u'dummy': 'dummy.Write'},
            IDummy.getTaggedValue(WRITE_PERMISSIONS_KEY)
        )

    def test_read_no_permissions(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy')

        handler = SecuritySchema()
        handler.read(field_node, IDummy, IDummy['dummy'])

        self.assertFalse(READ_PERMISSIONS_KEY in IDummy.getTaggedValueTags())
        self.assertFalse(WRITE_PERMISSIONS_KEY in IDummy.getTaggedValueTags())

    def test_write(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy')

        IDummy.setTaggedValue(READ_PERMISSIONS_KEY, {u'dummy': 'dummy.Read'})
        IDummy.setTaggedValue(WRITE_PERMISSIONS_KEY, {u'dummy': 'dummy.Write'})

        handler = SecuritySchema()
        handler.write(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(
            'dummy.Read',
            field_node.get(ns('read-permission', self.namespace))
        )
        self.assertEqual(
            'dummy.Write',
            field_node.get(ns('write-permission', self.namespace))
        )

    def test_write_no_permissions(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy')

        IDummy.setTaggedValue(READ_PERMISSIONS_KEY, {u'dummy': None})

        handler = SecuritySchema()
        handler.write(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(
            None,
            field_node.get(ns('read-permission', self.namespace))
        )
        self.assertEqual(
            None,
            field_node.get(ns('write-permission', self.namespace))
        )

    def test_write_no_metadata(self):
        field_node = etree.Element('field')

        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u'dummy')

        handler = SecuritySchema()
        handler.write(field_node, IDummy, IDummy['dummy'])

        self.assertEqual(
            None,
            field_node.get(ns('read-permission', self.namespace))
        )
        self.assertEqual(
            None,
            field_node.get(ns('write-permission', self.namespace))
        )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFormSchema))
    suite.addTest(unittest.makeSuite(TestSecuritySchema))
    return suite
