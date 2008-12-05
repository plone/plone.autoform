==============
plone.autoform
==============

This package provides tools to construct z3c.form forms out of hints stored
in tagged values on schema interfaces. A special form base class is used to
set up the 'fields' and 'groups' properties on form instances.

The tagged values are stored under a key represented by the following 
constant:

    >>> from plone.autoform.interfaces import FORMDATA_KEY

In addition, field groups are constructed from plone.supermodel fieldsets,
which are also stored in tagged values, under the following constant:

    >>> from plone.supermodel.interfaces import FIELDSETS_KEY

There are several ways to set the form data:

    - Manually, by using setTaggedValue() on an interface.

    - By loading the schema from a plone.supermodel XML file.
      
    - By using the grok directives in the plone.directives.dexterity package.

To use the automatic form setup, mix in the following base class in your
forms:

    >>> from plone.autoform.formbase import AutoExtensibleForm

and then provide the 'schema' (a schema interface) and optionally the
'additional_schemata' (a list of schema interfaces) attributes on your form:

    >>> class MyForm(AutoExtensibleForm, form.EditForm):
    ...     schema = IMySchema
    ...     additional_schemata = (ISchemaOne, ISchemaTwo,)
    ...     
    ...     # ...

For dynamic forms, you could of course make 'schema' and 'additional_schemata' 
into properties.

See autoform.txt for details on how to use the form generation, and
supermodel.txt for information on the 'form' XML namespace.