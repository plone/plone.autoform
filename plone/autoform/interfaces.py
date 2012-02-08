from zope.interface import Interface
from zope.interface.interfaces import IInterface

import zope.schema

from z3c.form.interfaces import IFieldsForm, IDisplayForm, IWidget
from plone.supermodel.interfaces import IFieldset

# Schema interface tagged value keys

OMITTED_KEY   = u"plone.autoform.omitted"
WIDGETS_KEY   = u"plone.autoform.widgets"
MODES_KEY     = u"plone.autoform.modes"
ORDER_KEY     = u"plone.autoform.order"

READ_PERMISSIONS_KEY  = u"plone.autoform.security.read-permissions"
WRITE_PERMISSIONS_KEY = u"plone.autoform.security.write-permissions"

# Supermodel namespace and prefix

FORM_NAMESPACE = 'http://namespaces.plone.org/supermodel/form'
FORM_PREFIX = 'form'

SECURITY_NAMESPACE = 'http://namespaces.plone.org/supermodel/security'
SECURITY_PREFIX = 'security'

class IFormFieldProvider(Interface):
    """Marker interface for schemata that provide form fields.
    """

class IAutoExtensibleForm(Interface):
    """The mixin class plone.autoform.form.AutoExtensibleForm can be
    used to have z3c.form forms that build automatically based on the contents
    of various tagged values, on multiple schema interfaces, which
    should be supplied with the properties defined below. See autoform.txt
    for details.
    """
    
    ignorePrefix = zope.schema.Bool(title=u"Do not set a prefix for additional schemata",
                                    default=False)
    
    schema = zope.schema.Object(title=u"Schema providing form fields",
                                schema=IInterface)
                                
    additionalSchemata = zope.schema.Tuple(title=u"Supplementary schemata providing additional form fields",
                                           value_type=zope.schema.Object(title=u"Schema interface",
                                                                          schema=IInterface),
                                           required=False)

class IAutoObjectSubForm(Interface):
    """This mixin class enables a form based on z3c.form.object.ObjectSubForm
    to also have its fields updated with form hints. See subform.txt
    """

    schema = zope.schema.Object(title=u"Schema providing form fields",
                                schema=IInterface)


class IWidgetsView(IAutoExtensibleForm, IFieldsForm, IDisplayForm):
    """A display form that supports setting up widgets based on schema
    interfaces.
    """
    
    w = zope.schema.Dict(title=u"Shortcut lookup for all widgets",
                         description=u"Contains all widgets, including "
                                      "those from groups within this form",
                         key_type=zope.schema.ASCIILine(title=u"Widget name, with prefix"),
                         value_type=zope.schema.Object(title=u"Widget", schema=IWidget))

    fieldsets = zope.schema.Dict(title=u"Lookup fieldset (group) by name",
                              key_type=zope.schema.ASCIILine(title=u"Fieldset name"),
                              value_type=zope.schema.Object(title=u"Fieldset", schema=IFieldset))
