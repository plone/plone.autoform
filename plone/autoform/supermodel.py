from z3c.form.interfaces import IFieldWidget, IValidator
from z3c.form.util import getSpecification
from z3c.form.validator import WidgetValidatorDiscriminators
from zope.component import provideAdapter
from zope.interface import implements, Interface
from zope.interface.interface import InterfaceClass

from plone.supermodel.utils import ns
from plone.supermodel.parser import IFieldMetadataHandler

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

from plone.autoform.interfaces import FORM_NAMESPACE, FORM_PREFIX
from plone.autoform.interfaces import SECURITY_NAMESPACE, SECURITY_PREFIX

from plone.autoform.utils import resolveDottedName

class FormSchema(object):
    """Support the form: namespace in model definitions.
    """
    implements(IFieldMetadataHandler)
    
    namespace = FORM_NAMESPACE
    prefix = FORM_PREFIX
    
    def _add(self, schema, key, name, value, expected=None):
        if expected is not None:
            obj = resolveDottedName(value)
            if not expected.implementedBy(obj):
                raise ValueError("%s not implemented by %s"
                    % (expected.__identifier__, value))
        tagged_value = schema.queryTaggedValue(key, {})
        tagged_value[name] = value
        schema.setTaggedValue(key, tagged_value)
    
    def _add_order(self, schema, name, direction, relative_to):
        tagged_value = schema.queryTaggedValue(ORDER_KEY, [])
        tagged_value.append((name, direction, relative_to,))
        schema.setTaggedValue(ORDER_KEY, tagged_value)
    
    def _add_interface_values(self, schema, key, name, values):
        tagged_value = schema.queryTaggedValue(key, [])
        values = values.split(' ')
        for value in values:
            if ':' in value:
                (interface_dotted_name, value) = value.split(':')
                interface = resolveDottedName(interface_dotted_name)
                if not isinstance(interface, InterfaceClass):
                    raise ValueError(
                        "%s not an Interface."% interface_dotted_name)
            else:
                interface = Interface
            tagged_value.append((interface, name, value))
        schema.setTaggedValue(key, tagged_value)
    
    def _add_validator(self, field, value):
        validator = resolveDottedName(value)
        if not IValidator.implementedBy(validator):
            raise ValueError(
                "z3c.form.interfaces.IValidator not implemented by %s."
                % value)
        provideAdapter(validator,
            (None, None, None, getSpecification(field), None),
            IValidator,
            )

    def read(self, fieldNode, schema, field):
        name = field.__name__
        
        widget    = fieldNode.get( ns('widget',    self.namespace) )
        mode      = fieldNode.get( ns('mode',      self.namespace) )
        omitted   = fieldNode.get( ns('omitted',   self.namespace) )
        before    = fieldNode.get( ns('before',    self.namespace) )
        after     = fieldNode.get( ns('after',     self.namespace) )
        validator = fieldNode.get( ns('validator', self.namespace) )

        if widget:
            self._add(schema, WIDGETS_KEY, name, widget, IFieldWidget)
        if mode:
            self._add_interface_values(schema, MODES_KEY, name, mode)
        if omitted:
            self._add_interface_values(schema, OMITTED_KEY, name, omitted)
        if before:
            self._add_order(schema, name, 'before', before)
        if after:
            self._add_order(schema, name, 'after', after)
        if validator:
            self._add_validator(field, validator)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        
        widget  = schema.queryTaggedValue(WIDGETS_KEY, {}).get(name, None)
        mode    = [(i,v) for i,n,v in schema.queryTaggedValue(MODES_KEY, []) if n == name]
        omitted = [(i,v) for i,n,v in schema.queryTaggedValue(OMITTED_KEY, []) if n == name]
        order   = [(d,v) for n,d,v in schema.queryTaggedValue(ORDER_KEY,  []) if n == name]
        
        if widget is not None:
            if not isinstance(widget, basestring):
                widget = "%s.%s" % (widget.__module__, widget.__name__)
            fieldNode.set(ns('widget', self.namespace), str(widget))
        
        mode_values = []
        for interface, value in mode:
            if interface is not Interface:
                value = "%s:%s" % (interface.__identifier__, value)
            mode_values.append(value)
        if mode_values:
            fieldNode.set(ns('mode', self.namespace), " ".join(mode_values))
        
        omitted_values = []
        for interface, value in omitted:
            if interface is not Interface:
                value = "%s:%s" % (interface.__identifier__, value)
            omitted_values.append(value)
        if omitted_values:
            fieldNode.set(ns('omitted', self.namespace), " ".join(omitted_values))

        for direction, relative_to in order:
            if direction == 'before':
                fieldNode.set(ns('before',  self.namespace), relative_to)
            elif direction == 'after':
                fieldNode.set(ns('after',  self.namespace), relative_to)

class SecuritySchema(object):
    """Support the security: namespace in model definitions.
    """
    implements(IFieldMetadataHandler)
    
    namespace = SECURITY_NAMESPACE
    prefix = SECURITY_PREFIX
    
    def read(self, fieldNode, schema, field):
        name = field.__name__
        
        read_permission = fieldNode.get(ns('read-permission', self.namespace))
        write_permission = fieldNode.get(ns('write-permission', self.namespace))
        
        read_permissions = schema.queryTaggedValue(READ_PERMISSIONS_KEY, {})
        write_permissions = schema.queryTaggedValue(WRITE_PERMISSIONS_KEY, {})
        
        if read_permission:
            read_permissions[name] = read_permission
            schema.setTaggedValue(READ_PERMISSIONS_KEY, read_permissions)
            
        if write_permission:
            write_permissions[name] = write_permission
            schema.setTaggedValue(WRITE_PERMISSIONS_KEY, write_permissions)

    def write(self, fieldNode, schema, field):
        name = field.__name__
        
        read_permission = schema.queryTaggedValue(READ_PERMISSIONS_KEY, {}).get(name, None)
        write_permission = schema.queryTaggedValue(WRITE_PERMISSIONS_KEY, {}).get(name, None)
        
        if read_permission:
            fieldNode.set(ns('read-permission', self.namespace), read_permission)
        if write_permission:
            fieldNode.set(ns('write-permission', self.namespace), write_permission)