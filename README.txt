==============
plone.autoform
==============

.. contents:: Contents

This package provides tools to construct `z3c.form`_ forms out of hints stored
in tagged values on schema interfaces. A special form base class is used to
set up the ``fields`` and ``groups`` properties on form instances. It also
contains a "display form" implementation that is compatible with Zope 2
page templates, and with some convenience features for rendering widgets in
view mode.

The tagged values are stored under a various keys. These can be found in
the ``plone.autoform.interfaces`` module. They support:

* changing a field to 'display' or 'hidden' mode
* omitting fields
* re-ordering fields relative to one another
* placing fields into fieldsets (groups)
* changing the widget of a field
* displaying a field conditionally based on a permission

There are several ways to set the form data:

* Manually, by using ``setTaggedValue()`` on an interface.
* By loading the schema from a `plone.supermodel`_ XML file and using the 
  ``form:`` prefix
* By using the grok directives in the `plone.directives.form`_ package.

To use the automatic form setup, mix in the following base class in your
forms::

    >>> from plone.autoform.form import AutoExtensibleForm

and then provide the ``schema``` (a schema interface) and optionally the
``additionalSchemata`` (a list of schema interfaces) attributes on your form::

    >>> class MyForm(AutoExtensibleForm, form.EditForm):
    ...     schema = IMySchema
    ...     additionalSchemata = (ISchemaOne, ISchemaTwo,)
    ...     
    ...     # ...

For dynamic forms, you could of course make ``schema`` and 
``additionalSchemata`` into properties.

To use the display form, create a view like:

    >>> from plone.autoform.view import WidgetsView
    >>> class MyView(WidgetsView):
    ...     schema = IMySchema
    ...     additionalSchemata = (ISchemaOne, ISchemaTwo,)
    ...     
    ...     # ...

To render the form, do not override ``__call__()``. Instead, either implement
the ``render()`` method, set an ``index`` attribute to a page template or
other callable, or use the ``template`` attribute of the ``<browser:page />``
ZCML directive when registering the view.

In the template, you can use the following variables:

* ``view/w`` is a dictionary of all widgets, including those from non-default
  fieldsets (by contrast, the ``widgets`` variable contains only those
  widgets in the default fieldset). The keys are the field names, and the
  values are widget instances. To render a widget (in display mode), you can
  do ``tal:replace="structure view/w/myfield/render" />``.
* ``view/fieldsets`` is a dictionary of all fieldsets (not including the
  default fieldset, i.e. those widgets not placed into a fieldset). They keys
  are the fieldset names, and the values are the fieldset form instances,
  which in turn have variables like ``widgets`` given a list of all widgets.

See ```autoform.txt``` for details on how to use the form generation,
``view.txt`` for details on the widgets view, and ``supermodel.txt`` for
information on the ``form`` XML namespace in a `plone.supermodel`_ schema
file.

.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _plone.z3cform: http://pypi.python.org/pypi/plone.z3cform
.. _plone.supermodel: http://pypi.python.org/pypi/plone.supermodel
.. _plone.directives.form: http://pypi.python.org/pypi/plone.directives.form
