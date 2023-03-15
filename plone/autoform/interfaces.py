from plone.supermodel.interfaces import IFieldset
from z3c.form.interfaces import IDisplayForm
from z3c.form.interfaces import IFieldsForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from zope.interface import Interface
from zope.interface.interfaces import IInterface

import zope.schema


# Schema interface tagged value keys
MODES_KEY = "plone.autoform.modes"
OMITTED_KEY = "plone.autoform.omitted"
ORDER_KEY = "plone.autoform.order"
WIDGETS_KEY = "plone.autoform.widgets"

READ_PERMISSIONS_KEY = "plone.autoform.security.read-permissions"
WRITE_PERMISSIONS_KEY = "plone.autoform.security.write-permissions"

# Supermodel namespace and prefix

FORM_NAMESPACE = "http://namespaces.plone.org/supermodel/form"
FORM_PREFIX = "form"

SECURITY_NAMESPACE = "http://namespaces.plone.org/supermodel/security"
SECURITY_PREFIX = "security"


class IFormFieldProvider(Interface):
    """Marker interface for schemata that provide form fields."""


class IAutoExtensibleForm(Interface):
    """The mixin class plone.autoform.form.AutoExtensibleForm can be
    used to have z3c.form forms that build automatically based on the contents
    of various tagged values, on multiple schema interfaces, which
    should be supplied with the properties defined below. See autoform.txt
    for details.
    """

    ignorePrefix = zope.schema.Bool(
        title="Do not set a prefix for additional schemata", default=False
    )

    schema = zope.schema.Object(title="Schema providing form fields", schema=IInterface)

    additionalSchemata = zope.schema.Tuple(
        title="Supplementary schemata providing additional form fields",
        value_type=zope.schema.Object(title="Schema interface", schema=IInterface),
        required=False,
    )


class IAutoObjectSubForm(Interface):
    """This mixin class enables a form based on z3c.form.object.ObjectSubForm
    to also have its fields updated with form hints. See subform.txt
    """

    schema = zope.schema.Object(title="Schema providing form fields", schema=IInterface)


class IWidgetsView(IAutoExtensibleForm, IFieldsForm, IDisplayForm):
    """A display form that supports setting up widgets based on schema
    interfaces.
    """

    w = zope.schema.Dict(
        title="Shortcut lookup for all widgets",
        description="Contains all widgets, including those from groups "
        "within this form",
        key_type=zope.schema.ASCIILine(title="Widget name, with prefix"),
        value_type=zope.schema.Object(title="Widget", schema=IWidget),
    )

    fieldsets = zope.schema.Dict(
        title="Lookup fieldset (group) by name",
        key_type=zope.schema.ASCIILine(title="Fieldset name"),
        value_type=zope.schema.Object(title="Fieldset", schema=IFieldset),
    )


class IParameterizedWidget(IFieldWidget):
    """A widget factory that can create a widget with parameters."""


class IWidgetExportImportHandler(Interface):
    """Supermodel export/import handler for widgets."""
