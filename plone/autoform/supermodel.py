from zope.interface import implements

from plone.supermodel.utils import ns
from plone.supermodel.parser import IFieldMetadataHandler

from plone.autoform.interfaces import FORMDATA_KEY
from plone.autoform.interfaces import SUPERMODEL_NAMESPACE, SUPERMODEL_PREFIX

class FormSchema(object):
    """Support the form: namespace in model definitions.
    """
    implements(IFieldMetadataHandler)
    
    namespace = SUPERMODEL_NAMESPACE
    prefix = SUPERMODEL_PREFIX
    
    def read(self, field_node, schema, field):
        name = field.__name__
        
        widget = field_node.get(ns('widget', self.namespace))
        mode = field_node.get(ns('mode', self.namespace))
        omitted = field_node.get(ns('omitted', self.namespace))
        before = field_node.get(ns('before', self.namespace))
        after = field_node.get(ns('after', self.namespace))
        
        settings = schema.queryTaggedValue(FORMDATA_KEY, {})
        updated = False
        
        if widget:
            settings.setdefault('widgets', []).append((name, widget))
            updated = True
        if mode:
            settings.setdefault('modes', []).append((name, mode))
            updated = True
        if omitted:
            settings.setdefault('omitted', []).append((name, omitted))
            updated = True
        if before:
            settings.setdefault('before', []).append((name, before))
            updated = True
        if after:
            settings.setdefault('after', []).append((name, after))
            updated = True
            
        if updated:
            schema.setTaggedValue(FORMDATA_KEY, settings)

    def write(self, field_node, schema, field):
        name = field.__name__
        
        settings = schema.queryTaggedValue(FORMDATA_KEY, {})
        
        widget = [v for n,v in settings.get('widgets', []) if n == name]
        mode = [v for n,v in settings.get('modes', []) if n == name]
        omitted = [v for n,v in settings.get('omitted', []) if n == name]
        before = [v for n,v in settings.get('before', []) if n == name]
        after = [v for n,v in settings.get('after', []) if n == name]
        
        if widget:
            field_node.set(ns('widget', self.namespace), widget[0])
        if mode:
            field_node.set(ns('mode', self.namespace), mode[0])
        if omitted:
            field_node.set(ns('omitted', self.namespace), omitted[0])
        if before:
            field_node.set(ns('before', self.namespace), before[0])
        if after:
            field_node.set(ns('after', self.namespace), after[0])