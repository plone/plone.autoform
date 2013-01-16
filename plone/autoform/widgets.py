from z3c.form.widget import FieldWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from plone.autoform.utils import resolveDottedName


@implementer(IFieldWidget)
class ParameterizedWidget(object):
    """A factory for deferred construction of widgets with parameters.

    z3c.form widgets are associated with a particular request,
    so they cannot be instantiated until the form is rendered.
    But it's often desired to use a widget with particular attributes set.

    This class acts as a "field widget" factory. It is instantiated
    at configuration time with a widget class and some parameters.
    Then it can be assigned to a z3c.form field's widgetFactory attribute
    or stored in the plone.autoform widget tagged value.
    Later, it is called by z3c.form with the Zope field and request
    and returns a widget instance with the desired parameters in place.

    Typically developers will not use this class directly,
    but will use the widget schema directive, the <widget /> directive
    in model XML, or the TTW UI to configure their parameterized widget.
    Those all use ParameterizedWidget internally.
    """
    
    def __init__(self, widget_factory=None, **params):
        if widget_factory is not None:
            if not IFieldWidget.implementedBy(widget_factory) \
            and not IWidget.implementedBy(widget_factory):
                raise TypeError('widget_factory must be an IFieldWidget or an IWidget')
        self.widget_factory = widget_factory
        self.params = params

    def __call__(self, field, request):
        if isinstance(self.widget_factory, basestring):
            self.widget_factory = resolveDottedName(self.widget_factory)

        if self.widget_factory is None:
            # use default widget factory for this field type
            widget = getMultiAdapter((field, request), IFieldWidget)
        elif IWidget.implementedBy(self.widget_factory):
            widget = FieldWidget(field, self.widget_factory(request))
        elif IFieldWidget.implementedBy(self.widget_factory):
            widget = self.widget_factory(field, request)
        for k, v in self.params.items():
            setattr(widget, k, v)
        return widget
