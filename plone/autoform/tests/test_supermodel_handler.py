import unittest

from zope.interface import Interface
import zope.schema

from plone.supermodel.utils import ns

from elementtree import ElementTree

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.supermodel import FormSchema

class TestFormSchema(unittest.TestCase):
    
    namespace = 'http://namespaces.plone.org/dexterity/form'
    
    def test_read(self):
        field_node = ElementTree.Element('field')
        field_node.set(ns("widget", self.namespace), "SomeWidget")
        field_node.set(ns("mode", self.namespace), "hidden")
        field_node.set(ns("omitted", self.namespace), "true")
        field_node.set(ns("before", self.namespace), "somefield")
        
        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u"dummy")
        
        handler = FormSchema()
        handler.read(field_node, IDummy, IDummy['dummy'])
        
        self.assertEquals({'dummy': 'SomeWidget'}, IDummy.getTaggedValue(WIDGETS_KEY))
        self.assertEquals({'dummy': 'true'}, IDummy.getTaggedValue(OMITTED_KEY))
        self.assertEquals({'dummy': 'hidden'}, IDummy.getTaggedValue(MODES_KEY))
        self.assertEquals([('dummy', 'before', 'somefield',)], IDummy.getTaggedValue(ORDER_KEY))

    def test_read_multiple(self):
        field_node1 = ElementTree.Element('field')
        field_node1.set(ns("widget", self.namespace), "SomeWidget")
        field_node1.set(ns("mode", self.namespace), "hidden")
        field_node1.set(ns("omitted", self.namespace), "true")
        field_node1.set(ns("before", self.namespace), "somefield")
        
        field_node2 = ElementTree.Element('field')
        field_node2.set(ns("mode", self.namespace), "display")
        field_node2.set(ns("omitted", self.namespace), "yes")
        
        class IDummy(Interface):
            dummy1 = zope.schema.TextLine(title=u"dummy1")
            dummy2 = zope.schema.TextLine(title=u"dummy2")
        
        handler = FormSchema()
        handler.read(field_node1, IDummy, IDummy['dummy1'])
        handler.read(field_node2, IDummy, IDummy['dummy2'])
    
        self.assertEquals({'dummy1': 'SomeWidget'}, IDummy.getTaggedValue(WIDGETS_KEY))
        self.assertEquals({'dummy1': 'true', 'dummy2': 'yes'}, IDummy.getTaggedValue(OMITTED_KEY))
        self.assertEquals({'dummy1': 'hidden', 'dummy2': 'display'}, IDummy.getTaggedValue(MODES_KEY))
        self.assertEquals([('dummy1', 'before', 'somefield',)], IDummy.getTaggedValue(ORDER_KEY))
    
    def test_read_no_data(self):
        field_node = ElementTree.Element('field')
        
        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u"dummy1")

        handler = FormSchema()
        handler.read(field_node, IDummy, IDummy['dummy'])
        
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        
    def test_write(self):
        field_node = ElementTree.Element('field')
        
        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u"dummy1")
            
        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy': 'SomeWidget'})
        IDummy.setTaggedValue(OMITTED_KEY, {'dummy': 'true'})
        IDummy.setTaggedValue(MODES_KEY, {'dummy': 'hidden'})
        IDummy.setTaggedValue(ORDER_KEY, [('dummy', 'before', 'somefield',)])
        
        handler = FormSchema()
        handler.write(field_node, IDummy, IDummy['dummy'])
        
        self.assertEquals("SomeWidget", field_node.get(ns("widget", self.namespace)))
        self.assertEquals("true", field_node.get(ns("omitted", self.namespace)))
        self.assertEquals("hidden", field_node.get(ns("mode", self.namespace)))
        self.assertEquals("somefield", field_node.get(ns("before", self.namespace)))
    
    def test_write_partial(self):
        field_node = ElementTree.Element('field')
        
        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u"dummy1")
        
        IDummy.setTaggedValue(WIDGETS_KEY, {'dummy': 'SomeWidget'})
        IDummy.setTaggedValue(OMITTED_KEY, {'dummy2': 'true'})
        IDummy.setTaggedValue(MODES_KEY, {'dummy': 'display', 'dummy2': 'hidden'})
        IDummy.setTaggedValue(ORDER_KEY, [])
        
        handler = FormSchema()
        handler.write(field_node, IDummy, IDummy['dummy'])
        
        self.assertEquals("SomeWidget", field_node.get(ns("widget", self.namespace)))
        self.assertEquals(None, field_node.get(ns("omitted", self.namespace)))
        self.assertEquals("display", field_node.get(ns("mode", self.namespace)))
        self.assertEquals(None, field_node.get(ns("before", self.namespace)))

    def test_write_no_data(self):
        field_node = ElementTree.Element('field')
        
        class IDummy(Interface):
            dummy = zope.schema.TextLine(title=u"dummy1")
            
        handler = FormSchema()
        handler.write(field_node, IDummy, IDummy['dummy'])
        
        self.assertEquals(None, field_node.get(ns("widget", self.namespace)))
        self.assertEquals(None, field_node.get(ns("omitted", self.namespace)))
        self.assertEquals(None, field_node.get(ns("mode", self.namespace)))
        self.assertEquals(None, field_node.get(ns("before", self.namespace)))
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFormSchema))
    return suite
