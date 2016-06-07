Changelog
=========

1.7.0 (2016-06-07)
------------------

Incompatibilities:

- Because of the ordering fix the field order in forms may be different.
  Before this fix the order was a gamble dependent on schema order.
  Schema form hints ``order_after`` and ``order_before`` may need minor adjustments.
  ``plone.autoform.utils.processFieldMoves`` was deprecated,
  but still works as before.
  The new functionality is now part of ``plone.autoform.base.AutoFields``.
  [jensens]

New:

- Fieldset labels/descriptions we're taken from first occurence.
  It was not possible to override them in a subsequent directive.
  Also it was not possible to set them in a subsequent directive, if it was not set before.
  Now subsequent directives w/o a label/description are just adding the field to the fieldset.
  If a different label and/or description is given, it replaces the existing prior loaded one.
  [jensens]

- The order of the fieldsets can be defined now explictly with the ``plone.supermodel.directives.fieldset`` directive.
  ``plone.autoform`` now does the sorting while fieldset processing.
  [jensens]

Fixes:

- Implementation on how field ordering happens was unreproducible if same schemas are coming in in different orders.
  New implementation build a well defined rule tree and processes then the field moves,
  almost independent from the schema order.
  [jensens]

- Update setup.py url
  [esteele]


1.6.2 (2016-02-20)
------------------

Fixes:

- Fix test for changed ``zope.interface`` comparison method, which
  incorrectly reports two different Interfaces from the same module
  but with empty name as being equal.  [thet]


1.6.1 (2014-10-20)
------------------

- pep8 cleanup, utf8-header,sorted imports, readability, ...
  [jensens]

- Fix issue where multiple (plone.supermodel) fieldset directive calls for the
  same fieldset name resulted to duplicate fieldsets (e.g. when updating
  fieldset with new fields in a subschema)
  [datakurre]


1.6 (2014-02-22)
----------------

- Replace deprecated test assert statements.
  [timo]

- Support anonymous schema (dynamic interfaces with and empty
  __name__ attribute) in autoGroups, opting to use prefix as
  group name for such cases.  This allows subclasses of
  AutoExtensibleForm to implement getPrefix() method as
  a sufficient condition to support an unnamed schema.
  [seanupton]


1.5 (2013-08-14)
----------------

- Added an option on form to allow display of empty fieldsets.
  [thomasdesvenain]

- fix tests
  [vangheem]


1.4 (2013-05-23)
----------------

- Enhance the widget directive to allow for specifying widget parameters
  within the schema.
  [davisagli]

- Support passing widget classes in the widget directive in addition to
  IFieldWidgets.
  [davisagli]

- Support serializing widget parameters to XML. This requires implementing
  a IWidgetExportImportHandler utility for the widget type.
  [davisagli]


1.3 (2012-08-30)
----------------

- Avoid dependency on z3c.form.testing.
  [hannosch]

1.2 (2012-04-15)
----------------

- Moved form schema directives here from plone.directives.form, and
  reimplemented them as plone.supermodel directives to avoid depending on
  grok.  Included directives: omitted, no_omit, mode, widget, order_before,
  order_after, read_permission, write_permission
  [davisagli]

1.1 - 2012-02-20
----------------

- Added the AutoObjectSubForm class to support form hints for
  object widget subforms.
  [jcbrand]

1.0 - 2011-05-13
----------------

- Raise a NotImplementedError instead of NotImplemented as that is not
  an exception but meant for comparisons and is not callable.
  [maurits]


1.0b7 - 2011-04-29
------------------

- Check to make sure that interfaces and field widgets resolved by the
  supermodel handler are of the correct type.
  [elro]

- Add form:validator support for supermodel.
  [elro]

- Fix issue where permission checks were not applied correctly to schemas being
  added with prefixes.
  [davisagli]

- Add MANIFEST.in.
  [WouterVH]


1.0b6 - 2011-02-11
------------------

- Fix WidgetsView so that _update and update do not clash.
  [elro]

- Fix view.txt doctest to test actual behaviour, not artifacts from test setup.
  [elro]


1.0b5 - 2011-01-11
------------------

- Use five.ManageSite permission to check field permissions. We'll avoid
  sniffing for Five/CMFCore permissions.zcml difference between Zope 2.12 and
  2.13. [esteele]


1.0b4 - 2010-08-05
------------------

- Fixed widget traversal for WidgetsView
  http://groups.google.com/group/dexterity-development/browse_frm/thread/280016ece3ed1462
  [29.08.2010, jbaumann]

- Make field permission checks use the field mode rather than the form mode.
  Fixes http://code.google.com/p/dexterity/issues/detail?id=110
  [optilude]

- Removed some dead code.
  Fixes http://code.google.com/p/dexterity/issues/detail?id=132
  [optilude, shywolf9982]


1.0b3 - 2010-04-20
------------------

- Properly handle the 'omitted' tagged value when it is set to 'false' for a
  field.
  [davisagli]

- Make it possible to set the 'omitted' and 'mode' settings only for particular
  form interfaces.
  [davisagli]

- Do not omit read-only fields when rendering a form in DISPLAY mode.
  http://code.google.com/p/dexterity/issues/detail?id=118
  [mj]


1.0b2 - 2009-07-12
------------------

- Changed API methods and arguments to mixedCase to be more consistent with
  the rest of Zope. This is a non-backwards-compatible change. Our profuse
  apologies, but it's now or never. :-/

  If you find that you get import errors or unknown keyword arguments in your
  code, please change names from foo_bar too fooBar, e.g. process_fields()
  becomes processFields().

  Note in particular that the additional_schemata property is now called
  additionalSchemata. If you have implemented this property yourself, you will
  need to rename it!
  [optilude]


1.0b1 - 2009-04-17
------------------

- Initial release
