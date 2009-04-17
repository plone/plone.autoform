==============
plone.autoform
==============

This package provides tools to construct z3c.form forms out of hints stored
in tagged values on schema interfaces. A special form base class is used to
set up the 'fields' and 'groups' properties on form instances. It also
contains a 'display form' implementation that is compatible with Zope 2
page templates, and with some convenience features for rendering widgets in
view mode.

The tagged values are stored under a various keys. These can be found in
the plone.autoform.interfaces module. They support:

 - changing a field to 'display' or 'hidden' mode
 - omitting fields
 - re-ordering fields relative to one another
 - placing fields into fieldsets (groups)
 - changing the widget of a field
 - displaying a field conditionally based on a permission

There are several ways to set the form data:

 - Manually, by using setTaggedValue() on an interface.
 - By loading the schema from a plone.supermodel XML file and using the 
   form: prefix
 - By using the grok directives in the plone.directives.form package.

To use the automatic form setup, mix in the following base class in your
forms:

    >>> from plone.autoform.form import AutoExtensibleForm

and then provide the 'schema' (a schema interface) and optionally the
'additional_schemata' (a list of schema interfaces) attributes on your form:

    >>> class MyForm(AutoExtensibleForm, form.EditForm):
    ...     schema = IMySchema
    ...     additional_schemata = (ISchemaOne, ISchemaTwo,)
    ...     
    ...     # ...

For dynamic forms, you could of course make 'schema' and 'additional_schemata' 
into properties.

To use the display form, create a view like:

    >>> from plone.autoform.view import WidgetsView
    >>> class MyView(WidgetsView):
    ...     schema = IMySchema
    ...     additional_schemata = (ISchemaOne, ISchemaTwo,)
    ...     
    ...     #

To render the form, do not override __call__(). Instead, either implement
the render() method or set an 'index' attribute to a page template or other
callable.

See autoform.txt for details on how to use the form generation, view.txt for
details on the widgets view, and supermodel.txt for information on the
'form' XML namespace in a plone.supermodel schema file.

