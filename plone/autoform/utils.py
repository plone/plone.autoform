from zope.component import queryUtility
from zope.interface import providedBy

from zope.security.interfaces import IPermission

from zope.dottedname.resolve import resolve

from z3c.form import field
from z3c.form.util import expandPrefix
from z3c.form.interfaces import IFieldWidget, INPUT_MODE, DISPLAY_MODE

from plone.supermodel.utils import mergedTaggedValueDict
from plone.supermodel.utils import mergedTaggedValueList

from plone.z3cform.fieldsets.group import GroupFactory

from plone.z3cform.fieldsets.utils import move

from plone.supermodel.interfaces import FIELDSETS_KEY

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

from AccessControl import getSecurityManager

_dottedCache = {}

def resolveDottedName(dottedName):
    """Resolve a dotted name to a real object
    """
    global _dottedCache
    if dottedName not in _dottedCache:
        _dottedCache[dottedName] = resolve(dottedName)
    return _dottedCache[dottedName]

def _getDisallowedFields(context, permissions, prefix):
    """Get a list of fields for which the user does not have the requisite
    permission. 'permissions' is a dict with field names as keys and
    permission names as values. The permission names will be looked up
    as IPermission utilities.
    """
    
    security_manager = getSecurityManager()
    
    disallowed = []
    permission_cache = {} # name -> True/False
    
    for fieldName, permission_name in permissions.items():
        if permission_name not in permission_cache:
            permission = queryUtility(IPermission, name=permission_name)
            if permission is None:
                permission_cache[permission_name] = True
            else:
                permission_cache[permission_name] = security_manager.checkPermission(permission.title, context)
        if not permission_cache[permission_name]:
            disallowed.append(_fn(prefix, fieldName))
    
    return disallowed

def mergedTaggedValuesForForm(schema, name, form):
    """Finds a list of (interface, fieldName, value) 3-ples from the tagged
    value named 'name', on 'schema' and all of its bases.  Returns a dict of
    fieldName => value, where the value is from the tuple for that fieldName
    whose interface is highest in the interface resolution order, among the
    interfaces actually provided by 'form'.
    """
    threeples = mergedTaggedValueList(schema, name)
    # filter out settings irrelevant to this form
    threeples = [t for t in mergedTaggedValueList(schema, name)
                 if t[0].providedBy(form)]
    # Sort by interface resolution order of the form interface,
    # then by IRO of the interface the value came from
    # (that is the input order, so we can rely on Python's stable sort)
    form_iro = list(providedBy(form).flattened())
    def by_form_iro(threeple):
        interface = threeple[0]
        return form_iro.index(interface)
    threeples.sort(key=by_form_iro)
    d = {}
    # Now iterate through in the reverse order -- the values assigned last win.
    for _, fieldName, value in reversed(threeples):
        d[fieldName] = value
    return d

# Some helper functions

def _fn(prefix, fieldName):
    """Give prefixed fieldname if applicable
    """
    if prefix:
        return expandPrefix(prefix) + fieldName
    else:
        return fieldName

def _bn(field):
    """Give base (non-prefixed) fieldname
    """
    prefix = field.prefix
    fieldName = field.__name__
    if prefix:
        return fieldName[len(prefix) + 1:]
    else:
        return fieldName

def _processWidgets(form, widgets, modes, newFields):
    """Update the fields list with widgets
    """

    for fieldName in newFields:
        field = newFields[fieldName]
        base_name = _bn(field)
        
        widget_name = widgets.get(base_name, None)
        widget_mode = modes.get(base_name, field.mode) or form.mode or INPUT_MODE
        
        widget_factory = None
        if widget_name is not None:
            if isinstance(widget_name, basestring):
                widget_factory = resolveDottedName(widget_name)
            elif IFieldWidget.implementedBy(widget_name):
                widget_factory = widget_name
            
            if widget_factory is not None:
                field.widgetFactory[widget_mode] = widget_factory
        
        if base_name in modes:
            newFields[fieldName].mode = widget_mode

def processFields(form, schema, prefix='', defaultGroup=None, permissionChecks=True):
    """Add the fields from the schema to the from, taking into account
    the hints in the various tagged values as well as fieldsets. If prefix
    is given, the fields will be prefixed with this prefix. If 
    defaultGroup is given (as a Fieldset instance), any field not explicitly
    placed into a particular fieldset, will be added to the given group,
    which must exist already. If permissionChecks is false,
    permission checks are ignored.
    """

    # Get data from tagged values, flattening data from super-interfaces
    
    # Note: The names always refer to a field in the schema, and never contain a prefix.
    
    omitted   = mergedTaggedValuesForForm(schema, OMITTED_KEY, form)   # { name => True }
    modes     = mergedTaggedValuesForForm(schema, MODES_KEY, form)     # { name => e.g. 'hidden' }
    widgets   = mergedTaggedValueDict(schema, WIDGETS_KEY)   # { name => widget/dotted name }

    fieldsets = mergedTaggedValueList(schema, FIELDSETS_KEY) # list of IFieldset instances

    # Get either read or write permissions depending on what type of form this is

    permissions = {}
    if permissionChecks:
        if form.mode == DISPLAY_MODE:
            permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)  # name => permission name
        elif form.mode == INPUT_MODE:
            permissions = mergedTaggedValueDict(schema, WRITE_PERMISSIONS_KEY) # name => permission name
    
    # Find the fields we should not worry about
    
    groups = {}
    do_not_process = list(form.fields.keys())
    do_not_process.extend(_getDisallowedFields(form.context, permissions, prefix))

    for fieldName, status in omitted.items():
        if status and status != 'false':
            do_not_process.append(_fn(prefix, fieldName))
    
    for group in form.groups:
        do_not_process.extend(list(group.fields.keys()))
        
        group_name = getattr(group, '__name__', group.label)
        groups[group_name] = group

    # Find all allowed fields so that we have something to select from
    omitReadOnly = form.mode != DISPLAY_MODE
    all_fields = field.Fields(schema, prefix=prefix, omitReadOnly=omitReadOnly).omit(*do_not_process)
    
    # Keep track of which fields are in a fieldset, and, by elimination,
    # which ones are not 
    
    fieldset_fields = []
    for fieldset in fieldsets:
        for fieldName in fieldset.fields:
            fieldset_fields.append(_fn(prefix, fieldName))
    
    # Set up the default fields, widget factories and widget modes
    
    newFields = all_fields.omit(*fieldset_fields)
    _processWidgets(form, widgets, modes, newFields)
    
    if not defaultGroup:
        form.fields += newFields
    else:
        groups[defaultGroup].fields += newFields
    
    # Set up fields for fieldsets
    
    for fieldset in fieldsets:
        
        newFields = all_fields.select(*[_fn(prefix, fieldName) 
                                            for fieldName in fieldset.fields
                                                if _fn(prefix, fieldName) in all_fields])
        
        if len(newFields) > 0:        
            _processWidgets(form, widgets, modes, newFields)
        
            if fieldset.__name__ not in groups:
                form.groups.append(GroupFactory(fieldset.__name__,
                                                label=fieldset.label,
                                                description=fieldset.description,
                                                fields=newFields))
            else:
                groups[fieldset.__name__].fields += newFields
    
    
def processFieldMoves(form, schema, prefix=''):
    """Process all field moves stored under ORDER_KEY in the schema tagged
    value. This should be run after all schemata have been processed with
    processFields().
    """
    
    order = mergedTaggedValueList(schema, ORDER_KEY)      # (name, 'before'/'after', other name)
            
    for fieldName, direction, relative_to in order:
        
        # Handle shortcut: leading . means "in this form". May be useful
        # if you want to move a field relative to one in the current
        # schema or (more likely) a base schema of the current schema, without
        # having to repeat the full prefix of this schema.

        if relative_to.startswith('.'):
            relative_to = relative_to[1:]
            if prefix:
                relative_to = expandPrefix(prefix) + relative_to
        
        try:
            if direction == 'before':
                move(form, fieldName, before=relative_to, prefix=prefix)
            elif direction == 'after':
                move(form, fieldName, after=relative_to, prefix=prefix)
        except KeyError:
            # The relative_to field doesn't exist
            pass