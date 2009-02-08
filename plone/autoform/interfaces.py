from zope.interface import Interface
from zope.interface.interfaces import IInterface

import zope.schema

# Schema interface tagged value keys

OMITTED_KEY      = u"plone.autoform.omitted"
WIDGETS_KEY      = u"plone.autoform.widgets"
MODES_KEY        = u"plone.autoform.modes"
ORDER_KEY        = u"plone.autoform.order"

SECURITY_KEY     = u"plone.autoform.security"

# Supermodel namespace and prefix

SUPERMODEL_NAMESPACE = 'http://namespaces.plone.org/dexterity/form'
SUPERMODEL_PREFIX = 'form'

class IFormFieldProvider(Interface):
    """Marker interface for schemata that provide form fields.
    """

class IAutoExtensibleForm(Interface):
    """The mixin class plone.autoform.formbase.AutoExtensibleForm can be
    used to have z3c.form forms that build automatically based on the contents
    of various tagged values, on multiple schema interfaces, which
    should be supplied with the properties defined below. See autoform.txt
    for details.
    """
    
    schema = zope.schema.Object(title=u"Schema providing form fields",
                                schema=IInterface)
                                
    additional_schemata = zope.schema.Tuple(title=u"Supplementary schemata providing additional form fields",
                                            value_type=zope.schema.Object(title=u"Schema interface",
                                                                          schema=IInterface),
                                            required=False)