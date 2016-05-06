# -*- coding: utf-8 -*-
from plone.autoform.interfaces import MODES_KEY
from plone.autoform.interfaces import OMITTED_KEY
from plone.autoform.interfaces import ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel.directives import DictCheckerPlugin
from plone.supermodel.directives import ListCheckerPlugin
from plone.supermodel.directives import MetadataDictDirective
from plone.supermodel.directives import MetadataListDirective
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from zope.interface import Interface
from zope.interface.interfaces import IInterface


class omitted(MetadataListDirective):
    """Directive used to omit one or more fields
    """
    key = OMITTED_KEY
    value = 'true'

    def factory(self, *args):
        if not args:
            raise TypeError(
                'The omitted directive expects at least one argument.'
            )
        form_interface = Interface
        if IInterface.providedBy(args[0]):
            form_interface = args[0]
            args = args[1:]
        return [(form_interface, field, self.value) for field in args]


class no_omit(omitted):
    """Directive used to prevent one or more fields from being omitted
    """
    value = 'false'


class OmittedPlugin(ListCheckerPlugin):

    key = OMITTED_KEY

    def fieldNames(self):
        if self.value is None:
            return
        for _, fieldName, _ in self.value:
            yield fieldName


class mode(MetadataListDirective):
    """Directive used to set the mode of one or more fields
    """
    key = MODES_KEY

    def factory(self, *args, **kw):
        if len(args) > 1:
            raise TypeError(
                'The mode directive expects 0 or 1 non-keyword arguments.'
            )
        form_interface = Interface
        if args:
            form_interface = args[0]
        return [(form_interface, field, mode) for field, mode in kw.items()]


class ModePlugin(OmittedPlugin):
    key = MODES_KEY


class widget(MetadataDictDirective):
    """Schema directive used to set the widget for one or more fields.

    Option 1:
       ``widget(field1='z3c.form.browser.text.TextWidget', field2=TextWidget)``

      The directive is passed keyword arguments mapping field names to widgets.
      The widget can be specified as either a widget class, or as a string
      with the dotted path to a widget class. It cannot be a widget instance,
      because a new widget instance needs to be constructed for each request.

      (For backwards-compatibility, the widget can also be specified as a field
      widget factory.  A ``field widget factory`` is a callable that returns a
      widget instance when passed a field and a request.)

    Option 2:
      ``widget('field1', TextWidget, label=u'My label')``

      This option makes it possible to configure a custom widget _and_
      customize its attributes.

      * The first positional arg is a string giving the name of a single field.
      * The second positional arg is a widget class, again specified as either
        a direct reference or a dotted path.
      * The remaining args are keyword arguments mapping arbitrary names to
        arbitrary values. These will be set as attributes of the widget when it
        is constructed.

    Option 3:
      ``widget('field1', label=u'My label')``

      This option makes it possible to _customize_ the field's default widget
      without naming it explicitly.

      * The first and only positional arg is a string giving the name of a
        single field.
      * The remaining args are keyword arguments mapping arbitrary names to
        arbitrary values.
        These will be set as attributes of the widget when it is constructed.
    """

    key = WIDGETS_KEY

    def factory(self, field_name=None, widget_class=None, **kw):
        widgets = {}

        if field_name is None:  # Usage 3
            for field_name, widget in kw.items():
                if not isinstance(widget, basestring):
                    widget = '{0}.{1}'.format(
                        widget.__module__,
                        widget.__name__
                    )
                widgets[field_name] = widget
        else:
            if widget_class is not None \
               and not IFieldWidget.implementedBy(widget_class) \
               and not IWidget.implementedBy(widget_class):
                raise TypeError(
                    'widget_class must implement IWidget or IFieldWidget'
                )
            widgets[field_name] = ParameterizedWidget(widget_class, **kw)

        return widgets


class WidgetPlugin(DictCheckerPlugin):
    key = WIDGETS_KEY


class order_before(MetadataListDirective):
    """Directive used to order one field before another
    """
    key = ORDER_KEY

    def factory(self, **kw):
        return [(field_name, 'before', relative_to)
                for field_name, relative_to in kw.items()]


class order_after(MetadataListDirective):
    """Directive used to order one field after another
    """
    key = ORDER_KEY

    def factory(self, **kw):
        return [(field_name, 'after', relative_to)
                for field_name, relative_to in kw.items()]


class OrderPlugin(ListCheckerPlugin):
    key = ORDER_KEY

    def fieldNames(self):
        if self.value is None:
            return
        for fieldName, _, _ in self.value:
            yield fieldName


class read_permission(MetadataDictDirective):
    """Directive used to set a field read permission
    """
    key = READ_PERMISSIONS_KEY

    def factory(self, **kw):
        return kw


class write_permission(read_permission):
    """Directive used to set a field write permission
    """
    key = WRITE_PERMISSIONS_KEY


class ReadPermissionsPlugin(DictCheckerPlugin):
    key = READ_PERMISSIONS_KEY


class WritePermissionsPlugin(DictCheckerPlugin):
    key = WRITE_PERMISSIONS_KEY
