# -*- coding: utf-8 -*-
from plone.autoform.base import AutoFields
from plone.autoform.interfaces import IAutoExtensibleForm
from plone.autoform.interfaces import IAutoObjectSubForm
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from zope.interface import implementer


_marker = object()


@implementer(IAutoExtensibleForm)
class AutoExtensibleForm(AutoFields, ExtensibleForm):
    """Mixin class for z3c.form forms that support fields extracted from
    a schema
    """

    showEmptyGroups = False

    @property
    def schema(self):
        raise NotImplementedError(
            'The class deriving from AutoExtensibleForm must have a '
            '\'schema\' property'
        )

    @property
    def additionalSchemata(self):
        """Default to there being no additional schemata
        """
        return ()

    def updateFields(self):
        self.updateFieldsFromSchemata()
        super(AutoExtensibleForm, self).updateFields()


@implementer(IAutoObjectSubForm)
class AutoObjectSubForm(AutoFields):
    """A Mixin class for z3c.form.object.ObjectSubForm forms that supports
    fields being updated from hints in a schema.
    """

    @property
    def schema(self):
        return self.__parent__.field.schema

    def setupFields(self):
        self.updateFieldsFromSchemata()
