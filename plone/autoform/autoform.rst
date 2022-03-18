Form setup details
==================

This package provides tools to construct z3c.form forms out of hints stored
in tagged values on schema interfaces. A special form base class is used to
set up the 'fields' and 'groups' properties on form instances.

The tagged values are stored under keys represented by the following
constants::

    >>> from plone.autoform.interfaces import OMITTED_KEY
    >>> from plone.autoform.interfaces import WIDGETS_KEY
    >>> from plone.autoform.interfaces import MODES_KEY
    >>> from plone.autoform.interfaces import ORDER_KEY
    >>> from plone.autoform.interfaces import READ_PERMISSIONS_KEY
    >>> from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY

In addition, field groups are constructed from plone.supermodel fieldsets,
which are also stored in tagged values, under the following constant::

    >>> from plone.supermodel.interfaces import FIELDSETS_KEY

There are several ways to set the form data:

* Manually, by using setTaggedValue() on an interface.
* By loading the schema from a plone.supermodel XML file. This package
  provides a schema handler for the 'form' prefix that can be used to
  incorporate form hints. See supermodel.txt for details.
* By using the directives from ``plone.autoform.directives`` while defining
  a schema in Python.

For the purposes of this test, we'll set the form data manually.

Test setup
----------

First, let's load this package's ZCML so that we can run the tests::

    >>> configuration = """\
    ... <configure xmlns="http://namespaces.zope.org/zope">
    ...
    ...     <include package="Products.Five" file="configure.zcml" />
    ...     <include package="plone.autoform" />
    ...
    ... </configure>
    ... """
    >>> import six
    >>> from six import StringIO
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(StringIO(configuration))

We also need a few sample interfaces::

    >>> from zope.interface import Interface
    >>> from zope import schema

    >>> class ITestSchema(Interface):
    ...     one = schema.TextLine(title=u"One")
    ...     two = schema.TextLine(title=u"Two")
    ...     three = schema.TextLine(title=u"Three")
    ...     four = schema.TextLine(title=u"Four")
    ...     five = schema.TextLine(title=u"Five")
    ...     six = schema.TextLine(title=u"Six")

    >>> class ISupplementarySchema(Interface):
    ...     one = schema.TextLine(title=u"One")
    ...     two = schema.TextLine(title=u"Two")

    >>> class IOtherSchema(Interface):
    ...     three = schema.TextLine(title=u"Three")
    ...     four = schema.TextLine(title=u"Four")
    ...     five = schema.TextLine(title=u"Five")
    ...     six = schema.TextLine(title=u"Six")

And a test context and request, marked with the ``IFormLayer`` interface to
make z3c.form happy::

    >>> from zope.publisher.browser import TestRequest
    >>> from z3c.form.interfaces import IFormLayer
    >>> context = object()
    >>> request = TestRequest(environ={'AUTHENTICATED_USER': 'user1'}, skin=IFormLayer)

Note that we need to pretend that we have authenticated a user. Without this,
the permission checks will be turned off. This is to support setting up a form
pre-traversal in the ++widget++ namespace in plone.z3cform.

And finally, a form::

    >>> from z3c.form.interfaces import IForm, IEditForm
    >>> from plone.autoform.form import AutoExtensibleForm
    >>> from z3c.form import form, button
    >>> class TestForm(AutoExtensibleForm, form.Form):
    ...     schema = ITestSchema
    ...     additionalSchemata = (ISupplementarySchema, IOtherSchema,)
    ...
    ...     ignoreContext = True

This form is in input mode::

    >>> TestForm.mode
    'input'

Adding form data
----------------

Form data can be held under the following keys:

OMITTED_KEY
    A list of (interface, fieldName, boolean) triples.
    If the third value evaluates to true,
    the field with the given fieldName will be omitted from forms providing the given interface.

MODES_KEY
    A list of (interface, fieldName, mode string) triples.
    A mode string may be one of the z3c.form widget modes,
    including 'hidden', 'input', and 'display'.
    The field will be rendered using a widget in the specified mode on forms providing the given interface.

WIDGETS_KEY
    A dict of fieldName => widget.
    The widget can be the dotted name of a z3c.form field widget factory,
    or an actual instance of one.

ORDER_KEY
    A list of (fieldName, direction, relative_to) triples.
    'direction' can be one of ``before`` or ``after``.
    relative_to can be ``*`` (any/all fields),
    or the name of a field to move the given field before or after in the form.

READ_PERMISSIONS_KEY
    A dict of fieldName => permission id.
    When a form is in 'display' mode,
    the field will be omitted unless the user has the given permission in the form's context.
    The permission id should be a Zope 3 style IPermission utility name,
    not a Zope 2 permission string.

WRITE_PERMISSIONS_KEY
    A dict of fieldName => permission id.
    When a form is in 'input' mode,
    the field will be omitted unless the user has the given permission in the form's context.
    The permission id should be a Zope 3 style IPermission utility name,
    not a Zope 2 permission string.

Note that 'order' directives are processed after all schemata in the form are
set up. Ordering will start by going through the additionalSchemata in order.
The form's base schema is processed last.

This means that the last ordering directive to be run is the last item in the
list in the form's base schema. Hence, this can be used to override any
ordering information from additional schemata.

The fieldName should never contain a prefix or a dot. However, the
relative_to name under ORDER_KEY should contain a prefixed name. The default
form schema will not have a prefix, but additional schemata will have a prefix
constructed from their ``__identifier__`` (full dotted name). To explicitly
reference a field in the current schema (or a base schema), use a leading
dot, e.g. ".title" would refer to the "title" field in the current schema,
whereas "title" would refer to the "title" field in the form's base schema.

Fieldset data is kept under the key defined in the constant ``FIELDSETS_KEY``.
This contains a list of ``plone.supermodel.model.Fieldset`` instances.

At this point, there is no form data. When the form is updated, the 'fields'
and 'groups' properties will be set.

::

    >>> test_form = TestForm(context, request)
    >>> test_form.update()
    >>> list(test_form.fields.keys())
    ['one', 'two', 'three', 'four', 'five', 'six',
     'ISupplementarySchema.one', 'ISupplementarySchema.two',
     'IOtherSchema.three', 'IOtherSchema.four',
     'IOtherSchema.five', 'IOtherSchema.six']
    >>> test_form.groups
    ()

Note how we have all the fields from all the schemata, and that the fields
from the additional schemata have been prefixed with the schema dotted name.

Let us now set up some form data.

Omitted fields are listed like this::

    >>> ITestSchema.setTaggedValue(OMITTED_KEY,
    ...                            ((IForm, 'four', True),
    ...                             (Interface, 'four', False),
    ...                             (Interface, 'five', False),
    ...                             (Interface, 'five', True))
    ...                           )

Field modes can be set like this::

    >>> ITestSchema.setTaggedValue(MODES_KEY,
    ...                            ((Interface, 'one', 'display'),
    ...                             (IEditForm, 'one', 'display'),
    ...                             (IForm, 'one', 'hidden'),
    ...                             (Interface, 'two', 'display'))
    ...                           )

Widgets can be specified either by a dotted name string or an actual instance::

    >>> from z3c.form.browser.password import PasswordFieldWidget
    >>> ITestSchema.setTaggedValue(WIDGETS_KEY, {'two': PasswordFieldWidget})
    >>> IOtherSchema.setTaggedValue(WIDGETS_KEY, {'five': 'z3c.form.browser.password.PasswordFieldWidget'})

Fields can be moved like this::

    >>> ITestSchema.setTaggedValue(
    ...     ORDER_KEY,
    ...     [('one', 'after', 'two')]
    ... )

    >>> IOtherSchema.setTaggedValue(
    ...     ORDER_KEY,
    ...     [
    ...         ('four', 'before', 'ISupplementarySchema.one'),
    ...         ('five', 'after', '.six',)
    ...     ]
    ... )

    >>> ISupplementarySchema.setTaggedValue(
    ...     ORDER_KEY,
    ...     [
    ...         ('one', 'before', '*'),
    ...         ('two', 'before', 'one')
    ...     ]
    ... )


    >>> test_form = TestForm(context, request)
    >>> test_form.update()
    >>> list(test_form.fields.keys())
    ['IOtherSchema.four',
    'ISupplementarySchema.one',
    'two',
    'ISupplementarySchema.two',
    'one',
    'three',
    'five',
    'six',
    'IOtherSchema.three',
    'IOtherSchema.six',
    'IOtherSchema.five']

Note how the second value of each tuple refers to the full name with a prefix,
so the field 'two' from ``ISupplementarySchema`` is moved before the field
'one' from the default (un-prefixed) ITestSchema. However, we move
``IOtherSchema``'s field 'five' after the field 'six' in the same schema by
using a shortcut: '.six' is equivalent to 'IOtherSchema.six' in this case.

Field permissions can be set like this::

    >>> ITestSchema.setTaggedValue(
    ...     WRITE_PERMISSIONS_KEY,
    ...     {'five': u'dummy.PermissionOne', 'six': u'five.ManageSite'}
    ... )

Note that if a permission is not found, the field will be allowed.

Finally, fieldsets are configured like this::

    >>> from plone.supermodel.model import Fieldset
    >>> ITestSchema.setTaggedValue(
    ...     FIELDSETS_KEY,
    ...     [Fieldset('fieldset1', fields=['three'],
    ...      label=u"Fieldset one",
    ...      description=u"Description of fieldset one")])
    >>> IOtherSchema.setTaggedValue(FIELDSETS_KEY, [Fieldset('fieldset1', fields=['three'])])

Note how the label/description need only be specified once.

The results of all of this can be seen below::


    >>> test_form = TestForm(context, request)
    >>> test_form.update()
    >>> list(test_form.fields.keys())
    ['IOtherSchema.four',
     'ISupplementarySchema.one',
     'two',
     'ISupplementarySchema.two',
     'one',
     'five',
     'IOtherSchema.six',
     'IOtherSchema.five']

The field ``ISupplementarySchema['one']`` was moved to the top of the form,
but then ``IOtherSchema['four']`` was moved before this one again.
``ITestSchema['one']`` was moved after ``ITestSchema['two']``.
``ISupplementarySchema['two']`` was then moved before ``ITestSchema['one']``,
coming between ``ITestSchema['one']`` and ``ITestSchema['two']``.

``ITestSchema['one']`` was hidden and ``ITestSchema['two']`` was put into
display mode::

    >>> test_form.widgets['one'].mode
    'hidden'
    >>> test_form.widgets['two'].mode
    'display'

``ITestSchema['two']`` and ``IOtherSchema['five']`` were both given a password
widget - one by instance, the other by dotted name::

    >>> test_form.widgets['two']
    <PasswordWidget 'form.widgets.two'>

    >>> test_form.widgets['IOtherSchema.five']
    <PasswordWidget 'form.widgets.IOtherSchema.five'>

There is one group corresponding to the fieldset where we put two fields. It
has taken the label and description from the first definition::

    >>> len(test_form.groups)
    1
    >>> test_form.groups[0].label
    'Fieldset one'
    >>> test_form.groups[0].description
    'Description of fieldset one'
    >>> list(test_form.groups[0].fields.keys())
    ['three', 'IOtherSchema.three']

Pre-traversal
-------------

plone.z3cform installs a ``++widget++`` namespace to allow traversal to
widgets. Unfortunately, traversal happens before authentication. Thus, all
security checks (read/write permissions) will fail.

To work around this, we ignore security checks if no authenticated user is
set in the request. Previously, we added one to the test request. If we
run the same tests without an authenticated user, the field 'six' should
return.

    >>> request = TestRequest(skin=IFormLayer)

    >>> test_form = TestForm(context, request)
    >>> test_form.update()
    >>> list(test_form.fields.keys())
    ['IOtherSchema.four', 'ISupplementarySchema.one', 'two',
    'ISupplementarySchema.two', 'one', 'five', 'six',
    'IOtherSchema.six', 'IOtherSchema.five']

Automatic field sets
--------------------

It is possible to create fieldsets automatically, on the principle of one
fieldset per schema. In this case, the fieldset name is the schema name,
the schema docstring becomes the schema description, and all fields in that
schema that are not explicitly assigned to another fieldset, will be in the
the per-schema fieldset.

    >>> class Basics(Interface):
    ...     """Basic metadata"""
    ...     title = schema.TextLine(title=u"Title")
    ...     description = schema.TextLine(title=u"Description")
    ...     creation_date = schema.Date(title=u"Creation date")
    ...     hidden_secret = schema.TextLine(title=u"Hidden secret!")

Let's change some field settings to ensure that they are still processed,
and move the creation_date field to another fieldset, which we will define
in full.

    >>> Basics.setTaggedValue(MODES_KEY, [(Interface, 'hidden_secret', 'hidden')])
    >>> Basics.setTaggedValue(FIELDSETS_KEY, [Fieldset('Dates', label="Cool dates", fields=['creation_date'])])

    >>> class Dates(Interface):
    ...     """Date information"""
    ...     start_date = schema.Date(title=u"Start date")
    ...     end_date = schema.Date(title=u"End date")

    >>> class Ownership(Interface):
    ...     """Ownership information"""
    ...     owner = schema.Date(title=u"The owner")

We can make a form of these schemata. For the sake of this demo, we'll also
set ``ignorePrefix`` to true, so that the form fields don't get a prefix. Note
that this may cause clashes if fields in different schemata share a name.

    >>> class CombiForm(AutoExtensibleForm, form.Form):
    ...     schema = Basics
    ...     additionalSchemata = (Dates, Ownership,)
    ...
    ...     ignoreContext = True
    ...     ignorePrefix = True
    ...     autoGroups = True

    >>> combi_form = CombiForm(context, request)
    >>> combi_form.update()

The default fields are those from the base schema, minus the one moved to
another fieldset.

    >>> list(combi_form.fields.keys())
    ['title', 'description', 'hidden_secret']

    >>> combi_form.widgets['hidden_secret'].mode
    'hidden'

Each additional schema then has its own fields. Note that setting the 'dates'
fieldset in the base schema had the effect of giving a more specific
label to the automatically created group for the Dates schema.

    >>> [(g.__name__, g.label, g.description, list(g.fields.keys()),) for g in combi_form.groups]
    [('Dates', 'Cool dates', None, ['creation_date', 'start_date', 'end_date']),
     ('Ownership', 'Ownership', 'Ownership information', ['owner'])]


It is possible to have interfaces/schema that have an empty __name__
attribute, specifically in some cases where a schema is dynamically
created.  In such cases, it is possible to have a subclass of
AutoExtensibleForm implement a getPrefix() function as a sufficient
condition for group naming when autoGroups is True.

    Define some unnamed schema:

    >>> class IUnknownName(Interface):
    ...     this = schema.TextLine()
    ...
    >>> IUnknownName.__name__ = ''  # dynamic schema, empty __name__

In any case, if we want to have a different anonymous schema, we have to create it using the InterfaceClass constructor.
The rare case of setting `__name__` or `__module__` is not supported in zope.interface >= 5 due to performance optimizations.
For more information also read:

- https://github.com/zopefoundation/zope.interface/issues/31
- https://github.com/zopefoundation/zope.interface/pull/183#issuecomment-599547556

::

    >>> from zope.interface.interface import InterfaceClass
    >>> IAnotherAnonymousSchema = InterfaceClass(
    ...     '',
    ...     (Interface,),
    ...     {'that': schema.TextLine(), '__module__': 'different.module'},
    ... )


    Create an extrinsicly stored name mapping:

    >>> nameToSchema = {
    ...     'groucho': IUnknownName,
    ...     'harpo': IAnotherAnonymousSchema,
    ... }
    ...
    >>> schemaToName = dict(reversed(t) for t in nameToSchema.items())

    And a form implementation that emits prefixes using above mapping:

    >>> class GroupNamingForm(AutoExtensibleForm, form.Form):
    ...     autoGroups = True
    ...     ignoreContext = True
    ...
    ...     schema = Interface
    ...     additionalSchemata = (IUnknownName, IAnotherAnonymousSchema)
    ...
    ...     def getPrefix(self, schema):
    ...         if schema in schemaToName:
    ...             return schemaToName.get(schema)
    ...         return super(GroupNamingForm, self).getPrefix(schema)
    ...

    >>> naming_form = GroupNamingForm(context, request)
    >>> naming_form.updateFieldsFromSchemata()
    >>> _getGroup = lambda factory: factory(context, request, None)
    >>> groups = [_getGroup(group) for group in naming_form.groups]
    >>> groups = dict((g.__name__, g) for g in groups)
    >>> names = tuple(sorted(group.__name__ for group in groups.values()))
    >>> assert names == ('groucho', 'harpo')
    >>> assert 'groucho.this' in groups['groucho'].fields
    >>> assert 'harpo.that' in groups['harpo'].fields
