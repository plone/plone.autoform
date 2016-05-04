# -*- coding: utf-8 -*-
from plone.autoform.base import AutoFields
from plone.autoform.interfaces import IWidgetsView
from plone.z3cform import z2
from z3c.form.form import DisplayForm
from z3c.form.interfaces import IFormLayer
from zope.interface import implementer


try:
    from Products.Five.bbb import AcquisitionBBB as Explicit
except ImportError:
    from Acquisition import Explicit


@implementer(IWidgetsView)
class WidgetsView(AutoFields, DisplayForm, Explicit):
    """Mix-in to allow widgets (in view mode) to be accesed from browser
    views.
    """

    # You should set one or more of these, or the 'fields' variable

    schema = None

    additionalSchemata = ()

    request_layer = IFormLayer

    w = None
    fieldsets = None

    def update(self):
        # The ++widget++ traverser only calls update, not __call__
        self._update()

    def render(self):
        if getattr(self, 'index', None) is not None:
            return self.index()
        raise NotImplementedError("You must implement the 'render' method")

    # Helper methods

    def __call__(self):
        # support subclassed forms which do not call update on their superclass
        self._update()
        self.update()
        return self.render()

    def _update(self):
        if self.w is not None:
            return

        z2.switch_on(self)
        self.updateFieldsFromSchemata()
        self.updateWidgets()

        # shortcut 'widget' dictionary for all fieldsets
        self.w = {}
        for k, v in self.widgets.items():
            self.w[k] = v

        groups = []
        self.fieldsets = {}

        for idx, groupFactory in enumerate(self.groups):
            group = groupFactory(self.context, self.request, self)
            group.update()

            for k, v in group.widgets.items():
                self.w[k] = v

            groups.append(group)

            group_name = getattr(group, '__name__', str(idx))
            self.fieldsets[group_name] = group

        self.groups = tuple(groups)
