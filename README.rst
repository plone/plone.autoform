plone.autoform
==============

.. contents:: Contents

Introduction
------------

``plone.autoform`` builds custom `z3c.form`_ forms based on a model (schema)
of what fields to include and what widgets and options should be used for each
field. This model is defined as a `zope.schema`_-based schema, but additional
hints can be supplied to control aspects of form display not normally specified
in a Zope schema.


Basic schema-based forms
------------------------

To use the automatic form setup, mix in the following base class in your
forms::

    >>> from plone.autoform.form import AutoExtensibleForm

and then provide the ``schema`` (a schema interface) and optionally the
``additionalSchemata`` (a list of schema interfaces) attributes on your form::

    class MyForm(AutoExtensibleForm, form.EditForm):
        schema = IMySchema
        additionalSchemata = (ISchemaOne, ISchemaTwo,)
        # ...

For dynamic forms, you could of course make ``schema`` and
``additionalSchemata`` into properties. For example, `plone.dexterity`_ extends the
basic AutoExtensibleForm so that ``schema`` is the content type schema and
``additionalSchemata`` is a list of field provider schemas associated with
behaviors.


Controlling form presentation
-----------------------------

Directives can be specified in the schema to control aspects of form presentation.

Changing a field's display mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A field's widget can be displayed in several "modes":

* input - allows the user to enter data into the field
* display - a read-only indication of the field's value
* hidden - a record of the field's value that is included only in the HTML source

The mode can be controlled using the ``mode`` directive::

    from plone.supermodel import model
    from plone.autoform import directives as form

    class IMySchema(model.Schema):

        form.mode(secret='hidden')
        form.mode(IEditForm, secret='input')
        secret = schema.TextLine(
            title=u"Secret",
            default=u"Secret stuff (except on edit forms)"
            )

In this case the mode for the ``secret`` field is set to 'hidden' for most forms,
but 'input' for forms that provide the IEditForm interface.

The corresponding supermodel XML directive is ``form:mode``::

    <field type="zope.schema.TextLine"
            name="secret"
            form:mode="z3c.form.interfaces.IForm:hidden z3c.form.interfaces.IEditForm:input">
        <title>Secret</title>
        <description>Secret stuff (except on edit forms)</description>
    </field>

The mode can be specified briefly if it should be the same for all forms::

    <field type="zope.schema.TextLine"
            name="secret"
            form:mode="hidden">
        <title>Secret</title>
        <description>Secret stuff</description>
    </field>

In other words, ``form:mode`` may be either a single mode, or a space-separated
list of form_interface:mode pairs.


Omitting fields
~~~~~~~~~~~~~~~

A field can be omitted entirely from all forms, or from some forms,
using the ``omitted`` and ``no_omit`` diretives. In this example,
the ``dummy`` field is omitted from all forms, and the ``edit_only``
field is omitted from all forms except those that provide the
IEditForm interface::

    from z3c.form.interfaces import IEditForm
    from plone.supermodel import model
    from plone.autoform import directives as form

    class IMySchema(model.Schema):

        form.omitted('dummy')
        dummy = schema.Text(
            title=u"Dummy"
            )

        form.omitted('edit_only')
        form.no_omit(IEditForm, 'edit_only')
        edit_only = schema.TextLine(
            title = u'Only included on edit forms',
            )

In supermodel XML, this can be specified as::

    <field type="zope.schema.TextLine"
           name="dummy"
           form:omitted="true">
        <title>Dummy</title>
    </field>

    <field type="zope.schema.TextLine"
           name="edit-only"
           form:omitted="z3c.form.interfaces.IForm:true z3c.form.interfaces.IEditForm:false">
        <title>Only included on edit form</title>
    </field>

``form:omitted`` may be either a single boolean value, or a space-separated
list of form_interface:boolean pairs.


Re-ordering fields
~~~~~~~~~~~~~~~~~~

A field's position in the form can be influenced using the ``order_before``
and ``order_after`` directives. In this example, the ``not_last`` field
is placed before the ``summary`` field even though it is defined afterward::

    from plone.supermodel import model
    from plone.autoform import directives as form

    class IMySchema(model.Schema):

        summary = schema.Text(
            title=u"Summary",
            description=u"Summary of the body",
            readonly=True
            )

        form.order_before(not_last='summary')
        not_last = schema.TextLine(
            title=u"Not last",
            )

The value passed to the directive may be either '*' (indicating before or after
all fields) or the name of another field. Use ``'.fieldname'`` to refer to
field in the current schema or a base schema. Prefix with the schema name (e.g.
``'IDublinCore.title'``) to refer to a field in another schema. Use an
unprefixed name to refer to a field in the current or the default schema for
the form.

In supermodel XML, the directives are called ``form:before`` and ``form:after``.
For example::

    <field type="zope.schema.TextLine"
           name="not_last"
           form:before="*">
        <title>Not last</title>
    </field>


Organizing fields into fieldsets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fields can be grouped into fieldsets, which will be rendered within an HTML
``<fieldset>`` tag. In this example the ``footer`` and ``dummy`` fields
are placed within the ``extra`` fieldset::

    from plone.supermodel import model
    from plone.autoform import directives as form

    class IMySchema(model.Schema):

        model.fieldset('extra',
            label=u"Extra info",
            fields=['footer', 'dummy']
            )

        footer = schema.Text(
            title=u"Footer text",
            )

        dummy = schema.Text(
            title=u"Dummy"
            )

In supermodel XML fieldsets are specified by grouping fields within a
``<fieldset>`` tag::

  <fieldset name="extra" label="Extra info">
      <field name="footer" type="zope.schema.TextLine">
          <title>Footer text</title>
      </field>
      <field name="dummy" type="zope.schema.TextLine">
          <title>Dummy</title>
      </field>
  </fieldset>


Changing a field's widget
~~~~~~~~~~~~~~~~~~~~~~~~~

Usually, z3c.form picks a widget based on the type of your field.
You can change the widget using the ``widget`` directive if you want
users to enter or view data in a different format. For example,
here we change the widget for the ``human`` field to use yes/no
radio buttons instead of a checkbox::

    from plone.supermodel import model
    from plone.autoform import directives as form
    from z3c.form.browser.radio import RadioFieldWidget

    class IMySchema(model.Schema):
        form.widget('human', RadioFieldWidget)
        human = schema.Bool(
            title = u'Are you human?',
            )

You can also pass widget parameters to control attributes of the
widget. For example, here we keep the default widget, but
set a CSS class::

    from plone.supermodel import model
    from plone.autoform import directives as form
    from z3c.form.browser.radio import RadioWidget

    class IMySchema(model.Schema):
        form.widget('human', klass='annoying')
        human = schema.Bool(
            title = u'Are you human?',
            )

In supermodel XML the widget is specified using a ``<form:widget>`` tag, which
can have its own elements specifying parameters::

    <field name="human" type="zope.schema.TextLine">
        <title>Are you human?</title>
        <form:widget type="z3c.form.browser.radio.RadioWidget">
            <klass>annoying</klass>
        </form:widget>
    </field>

Note: In order to be included in the XML representation of a schema,
widget parameters must be handled by a WidgetExportImportHandler utility.
There is a default one which handles the attributes defined in
``z3c.form.browser.interfaces.IHTMLFormElement``.

Protect a field with a permission
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, fields are included in the form regardless of the user's
permissions. Fields can be protected using the ``read_permission``
and ``write_permission`` directives. The read permission is checked when
the field is in display mode, and the write permission is checked when
the field is in input mode. The permission should be given with its
Zope 3-style name (i.e. cmf.ManagePortal rather than 'Manage portal').

In this example, the ``secret`` field is protected by the
``cmf.ManagePortal`` permission as both a read and write permission.
This means that in both display and input modes, the field will
only be included in the form for users who have that permission::

    from plone.supermodel import model
    from plone.autoform import directives as form

    class IMySchema(model.Schema):
        form.read_permission(secret='cmf.ManagePortal')
        form.write_permission(secret='cmf.ManagePortal')
        secret = schema.TextLine(
            title = u'Secret',
            )

In supermodel XML the directives are ``security:read-permission`` and
``security:write-permission``::

    <field type="zope.schema.TextLine"
           name="secret"
           security:read-permission="cmf.ManagePortal"
           security:write-permission="cmf.ManagePortal">
        <title>Secret</title>
    </field>

Display Forms
-------------

Sometimes rather than rendering a form for data entry, you want to display
stored values based on the same schema. This can be done using a "display form."
The display form renders each field's widget in "display mode," which means
that it shows the field value in read-only form rather than as a form input.

To use the display form, create a view that extends ``WidgetsView`` like this:

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


Behind the scenes: how autoform directives work
-----------------------------------------------

Zope schema fields do not allow storing arbitrary key-value data associated
with a particular field. However, arbitrary data can be stored in a
dictionary on the schema (interface) known as the "tagged values."
This is where ``plone.autoform`` keeps track of its extra hints,
whether they are configured via Python directives, an XML model, or some
other way.

The tagged values are stored under various keys, which are defined
in the ``plone.autoform.interfaces`` module. They can be set several ways:

* Manually, by using ``setTaggedValue()`` on an interface.
* By loading the schema from a `plone.supermodel`_ XML file and using the
  ``form:`` prefix
* By using the directives from ``plone.autoform.directives`` while defining
  a schema in Python.

Source Code
===========

Contributors please read the document `Process for Plone core's development <http://docs.plone.org/develop/plone-coredev/index.html>`_

Sources are at the `Plone code repository hosted at Github <https://github.com/plone/plone.autoform>`_.


.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _plone.supermodel: http://pypi.python.org/pypi/plone.supermodel
.. _plone.dexterity: http://pypi.python.org/pypi/plone.dexterity
