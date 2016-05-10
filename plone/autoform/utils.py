# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.autoform.interfaces import IParameterizedWidget
from plone.autoform.interfaces import MODES_KEY
from plone.autoform.interfaces import OMITTED_KEY
from plone.autoform.interfaces import ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.supermodel.interfaces import DEFAULT_ORDER
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.utils import mergedTaggedValueDict
from plone.supermodel.utils import mergedTaggedValueList
from plone.z3cform.fieldsets.group import GroupFactory
from plone.z3cform.fieldsets.utils import move
from z3c.form import field
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.util import expandPrefix
from zope.component import queryUtility
from zope.deprecation import deprecate
from zope.dottedname.resolve import resolve
from zope.interface import providedBy
from zope.security.interfaces import IPermission


_dottedCache = {}


def resolveDottedName(dottedName):
    """Resolve a dotted name to a real object
    """
    global _dottedCache
    if dottedName not in _dottedCache:
        _dottedCache[dottedName] = resolve(dottedName)
    return _dottedCache[dottedName]


def mergedTaggedValuesForIRO(schema, name, iro):
    """Finds a list of (interface, fieldName, value) 3-ples from the tagged
    value named 'name', on 'schema' and all of its bases.  Returns a dict of
    fieldName => value, where the value is from the tuple for that fieldName
    whose interface is highest in the interface resolution order, among the
    interfaces actually provided by 'form'.
    """
    # filter out settings irrelevant to this form
    threeples = [t for t in mergedTaggedValueList(schema, name)
                 if t[0] in iro]

    # Sort by interface resolution order of the form interface,
    # then by IRO of the interface the value came from
    # (that is the input order, so we can rely on Python's stable sort)
    def by_iro(threeple):
        interface = threeple[0]
        return iro.index(interface)
    threeples.sort(key=by_iro)
    d = {}
    # Now iterate through in the reverse order -- the values assigned last win.
    for _, fieldName, value in reversed(threeples):
        d[fieldName] = value
    return d


def mergedTaggedValuesForForm(schema, name, form):
    form_iro = list(providedBy(form).flattened())
    return mergedTaggedValuesForIRO(schema, name, form_iro)


# Some helper functions

def _process_prefixed_name(prefix, fieldName):
    """Give prefixed fieldname if applicable
    """
    if prefix:
        return expandPrefix(prefix) + fieldName
    else:
        return fieldName


def _bn(fieldInstance):
    """Base Name: Give base (non-prefixed) fieldname
    """
    prefix = fieldInstance.prefix
    fieldName = fieldInstance.__name__
    if prefix:
        return fieldName[len(prefix) + 1:]
    else:
        return fieldName


def _process_widgets(form, widgets, modes, newFields):
    """Update the fields list with widgets
    """

    for fieldName in newFields:
        fieldInstance = newFields[fieldName]
        baseName = _bn(fieldInstance)

        widgetName = widgets.get(baseName, None)
        widgetMode = modes.get(baseName, fieldInstance.mode) \
            or form.mode \
            or INPUT_MODE

        widgetFactory = None
        if widgetName is not None:
            if isinstance(widgetName, basestring):
                widgetFactory = resolveDottedName(widgetName)
            elif IFieldWidget.implementedBy(widgetName):
                widgetFactory = widgetName
            elif IParameterizedWidget.providedBy(widgetName):
                widgetFactory = widgetName

            if widgetFactory is not None:
                fieldInstance.widgetFactory[widgetMode] = widgetFactory

        if baseName in modes:
            newFields[fieldName].mode = widgetMode


def _process_fieldsets(
    form,
    schema,
    groups,
    all_fields,
    prefix,
    default_group
):
    """ Keep track of which fields are in a fieldset, and, by elimination,
    which ones are not
    """
    # { name => e.g. 'hidden' }
    modes = mergedTaggedValuesForForm(schema, MODES_KEY, form)

    # { name => widget/dotted name }
    widgets = mergedTaggedValueDict(schema, WIDGETS_KEY)

    # list of IFieldset instances
    fieldsets = mergedTaggedValueList(schema, FIELDSETS_KEY)

    # process primary schema fieldsets
    fieldset_fields = []
    for fieldset in fieldsets:
        for field_name in fieldset.fields:
            fieldset_fields.append(_process_prefixed_name(prefix, field_name))

    # Set up the default fields, widget factories and widget modes
    new_fields = all_fields.omit(*fieldset_fields)
    _process_widgets(form, widgets, modes, new_fields)

    if not default_group:
        form.fields += new_fields
    else:
        groups[default_group].fields += new_fields

    # Set up fields for fieldsets

    for fieldset in fieldsets:
        new_fields = all_fields.select(
            *[_process_prefixed_name(prefix, name) for name in fieldset.fields
              if _process_prefixed_name(prefix, name) in all_fields]
        )
        if not (
            getattr(form, 'showEmptyGroups', False) or
            len(new_fields) > 0
        ):
            continue
        _process_widgets(form, widgets, modes, new_fields)
        if fieldset.__name__ not in groups:
            group = GroupFactory(fieldset.__name__,
                                 label=fieldset.label,
                                 description=fieldset.description,
                                 order=fieldset.order,
                                 fields=new_fields)
            form.groups.append(group)
            groups[group.__name__] = group
        else:
            group = groups[fieldset.__name__]
            group.fields += new_fields
            if (
                fieldset.label and
                group.label != fieldset.label and
                group.__name__ != fieldset.label  # defaults to name!
            ):
                group.label = fieldset.label
            if (
                fieldset.description and
                group.description != fieldset.description
            ):
                group.description = fieldset.description
            if (
                fieldset.order and
                fieldset.order != DEFAULT_ORDER and
                fieldset.order != group.order
            ):
                group.order = fieldset.order


def _process_permissions(schema, form, all_fields):
    # Get either read or write permissions depending on what type of
    # form this is
    permission_cache = {}  # permission name -> allowed/disallowed

    # name => permission name
    read_permissions = mergedTaggedValueDict(
        schema,
        READ_PERMISSIONS_KEY
    )
    # name => permission name
    write_permissions = mergedTaggedValueDict(
        schema,
        WRITE_PERMISSIONS_KEY
    )
    security_manager = getSecurityManager()
    disallowed_fields = []

    for field_name, field_instance in all_fields.items():
        field_mode = field_instance.mode or form.mode
        permission_name = None
        base_name = _bn(field_instance)
        if field_mode == DISPLAY_MODE:
            permission_name = read_permissions.get(base_name, None)
        elif field_mode == INPUT_MODE:
            permission_name = write_permissions.get(base_name, None)
        if permission_name is None:
            continue
        if permission_name not in permission_cache:
            permission = queryUtility(IPermission, name=permission_name)
            if permission is None:
                permission_cache[permission_name] = True
            else:
                permission_cache[permission_name] = bool(
                    security_manager.checkPermission(
                        permission.title,
                        form.context
                    )
                )
        if not permission_cache.get(permission_name, True):
            disallowed_fields.append(field_name)

    return all_fields.omit(*disallowed_fields)


def processFields(form, schema, prefix='', defaultGroup=None,
                  permissionChecks=True):
    """Add the fields from the schema to the form, taking into account
    the hints in the various tagged values as well as fieldsets. If prefix
    is given, the fields will be prefixed with this prefix. If
    defaultGroup is given (as a Fieldset instance), any field not explicitly
    placed into a particular fieldset, will be added to the given group,
    which must exist already. If permissionChecks is false,
    permission checks are ignored.
    """

    # Get data from tagged values, flattening data from super-interfaces

    # Note: The names always refer to a field in the schema, and never
    # contain a prefix.

    # { name => True }
    omitted = mergedTaggedValuesForForm(schema, OMITTED_KEY, form)

    # Find the fields we should not worry about
    groups = {}
    do_not_process = list(form.fields.keys())

    for field_name, status in omitted.items():
        if status and status != 'false':
            do_not_process.append(_process_prefixed_name(prefix, field_name))

    for group in form.groups:
        do_not_process.extend(list(group.fields.keys()))
        groups[getattr(group, '__name__', group.label)] = group

    # Find all allowed fields so that we have something to select from
    omit_read_only = form.mode != DISPLAY_MODE
    all_fields = field.Fields(
        schema,
        prefix=prefix,
        omitReadOnly=omit_read_only
    ).omit(*do_not_process)

    if permissionChecks:
        all_fields = _process_permissions(schema, form, all_fields)
    _process_fieldsets(form, schema, groups, all_fields, prefix, defaultGroup)


@deprecate(
    'processFieldMoves must not be used any longer. Its implementation is '
    'unreproducible if same schemas are coming in in different orders. '
    'The new solution is part of the base.AutoFields class and does '
    'follow strict rules by first creating a rule dependency tree.'
    'This function will be remove in a 2.0 releaese and kept until then for '
    'backward compatibility reasons.'
)
def processFieldMoves(form, schema, prefix=''):
    """Process all field moves stored under ORDER_KEY in the schema tagged
    value. This should be run after all schemata have been processed with
    processFields().
    """

    # (name, 'before'/'after', other name)
    order = mergedTaggedValueList(schema, ORDER_KEY)
    for field_name, direction, relative_to in order:

        # Handle shortcut: leading . means 'in this schema'. May be useful
        # if you want to move a field relative to one in the current
        # schema or (more likely) a base schema of the current schema, without
        # having to repeat the full prefix of this schema.

        if relative_to.startswith('.'):
            relative_to = relative_to[1:]
            if prefix:
                relative_to = expandPrefix(prefix) + relative_to

        try:
            if direction == 'before':
                move(form, field_name, before=relative_to, prefix=prefix)
            elif direction == 'after':
                move(form, field_name, after=relative_to, prefix=prefix)
        except KeyError:
            # The relative_to field doesn't exist
            pass
