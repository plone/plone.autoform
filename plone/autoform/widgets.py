# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IParameterizedWidget
from plone.autoform.interfaces import IWidgetExportImportHandler
from plone.autoform.utils import resolveDottedName
from plone.supermodel.utils import elementToValue
from plone.supermodel.utils import noNS
from plone.supermodel.utils import valueToElement
from z3c.form.browser.interfaces import IHTMLFormElement
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import providedBy
from zope.schema import getFields

import z3c.form.browser.interfaces


@implementer(IParameterizedWidget)
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
                    and not IWidget.implementedBy(widget_factory) \
                    and not isinstance(widget_factory, basestring):
                raise TypeError('widget_factory must be an IFieldWidget '
                                'or an IWidget')
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

    def __repr__(self):
        return '{0}({1}, {2})'.format(
            self.__class__.__name__,
            self.widget_factory,
            self.params
        )

    def getWidgetFactoryName(self):
        """Returns the dotted path of the widget factory for serialization.

        Or None, if widget_factory is None.
        """
        widget = self.widget_factory
        if widget is None:
            return
        if not isinstance(widget, basestring):
            widget = '{0}.{1}'.format(widget.__module__, widget.__name__)
        return widget

    def getExportImportHandler(self, field):
        """Returns an IWidgetExportImportHandler suitable for this widget."""
        widgetName = self.getWidgetFactoryName()
        if widgetName is None:
            # Find default widget factory for this field.
            # We use lookup instead of getAdapter b/c we don't want to
            # instantiate the widget.
            sm = getSiteManager()
            widgetFactory = sm.adapters.lookup(
                (providedBy(field), IFormLayer), IFieldWidget)
            if widgetFactory is not None:
                widgetName = '{0}.{1}'.format(
                    widgetFactory.__module__,
                    widgetFactory.__name__
                )
            else:
                widgetName = u''

        widgetHandler = queryUtility(IWidgetExportImportHandler,
                                     name=widgetName)
        if widgetHandler is None:
            widgetHandler = WidgetExportImportHandler(IHTMLFormElement)
        return widgetHandler


@implementer(IWidgetExportImportHandler)
class WidgetExportImportHandler(object):

    def __init__(self, widget_schema):
        self.fieldAttributes = getFields(widget_schema)

    def read(self, widgetNode, params):
        for attributeName, attributeField in self.fieldAttributes.items():
            for node in widgetNode.iterchildren():
                if noNS(node.tag) == attributeName:
                    params[attributeName] = elementToValue(
                        attributeField,
                        node
                    )

    def write(self, widgetNode, params):
        for attributeName, attributeField in self.fieldAttributes.items():
            elementName = attributeField.__name__
            value = params.get(elementName, attributeField.default)
            if value != attributeField.default:
                child = valueToElement(attributeField, value, name=elementName)
                widgetNode.append(child)


TextAreaWidgetExportImportHandler = WidgetExportImportHandler(
    z3c.form.browser.interfaces.IHTMLTextAreaWidget
)
