from zope.interface import Interface
from zope.interface.interfaces import IInterface

import zope.schema

FORMDATA_KEY = u"plone.autoform"
SUPERMODEL_NAMESPACE = 'http://namespaces.plone.org/dexterity/form'
SUPERMODEL_PREFIX = 'form'

class IFormFieldProvider(Interface):
    """Marker interface for schemata that provide form fields.
    """

class IAutoExtensibleForm(Interface):
    """The mixin class plone.autoform.formbase.AutoExtensibleForm can be
    used to have z3c.form forms that build automatically based on the contents
    of the FORMDATA_KEY tagged value on various schema interfaces, which
    should be supplied with the properties defined below.
    
    The FORMDATA_KEY tagged value can be loaded from a plone.supermodel
    XML schema with the 'form' namespace (see supermodel), or it can be
    set manually. It should be a dictionary with the following keys:
    
        'widgets' -- dotted names of widget factories to use for 
            various fields.
        
        'modes' -- a widget mode, e.g. 'hidden'
        
        'omitted' -- fields to omit from the form; the value part should be
            a non-empty string
        
        'before' -- used to move fields; the value part is the name of another
            field, before which the given field will be moved
        
    Under each key is a list of (fieldname, value) pairs, where fieldname
    refers to the name of a schema field, and value is a string specific
    to the key.
    """
    
    schema = zope.schema.Object(title=u"Schema providing form fields",
                                schema=IInterface)
                                
    additional_schemata = zope.schema.Tuple(title=u"Supplementary schemata providing additional form fields",
                                            value_type=zope.schema.Object(title=u"Schema interface",
                                                                          schema=IInterface),
                                            required=False)