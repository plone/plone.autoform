from zope.interface import implements

from plone.z3cform.fieldsets.extensible import ExtensibleForm

from plone.autoform.interfaces import IAutoExtensibleForm
from plone.autoform.interfaces import IAutoObjectSubForm
from plone.autoform.base import AutoFields

_marker = object()

class AutoExtensibleForm(AutoFields, ExtensibleForm):
    """Mixin class for z3c.form forms that support fields extracted from
    a schema
    """

    implements(IAutoExtensibleForm)
    
    @property
    def schema(self):
        raise NotImplementedError("The class deriving from AutoExtensibleForm must have a 'schema' property")

    @property
    def additionalSchemata(self):
        """Default to there being no additional schemata
        """
        return ()
    
    def updateFields(self):
        self.updateFieldsFromSchemata()
        super(AutoExtensibleForm, self).updateFields()


class AutoObjectSubForm(AutoFields):
    """A Mixin class for z3c.form.object.ObjectSubForm forms that supports fields being
    updated from hints in a schema.
    """

    implements(IAutoObjectSubForm)

    @property
    def schema(self):
        return self.__parent__.field.schema

    def setupFields(self):
        self.updateFieldsFromSchemata()

