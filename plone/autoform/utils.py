from zope.component import queryUtility

from zope.security.interfaces import IPermission

from zope.dottedname.resolve import resolve

from z3c.form import field
from z3c.form.util import expandPrefix
from z3c.form.interfaces import IFieldWidget, INPUT_MODE, DISPLAY_MODE

from plone.supermodel.utils import merged_tagged_value_dict
from plone.supermodel.utils import merged_tagged_value_list

from plone.z3cform.fieldsets.group import GroupFactory

from plone.z3cform.fieldsets.utils import move

from plone.supermodel.interfaces import FIELDSETS_KEY

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

from AccessControl import getSecurityManager

_dotted_cache = {}

def resolve_dotted_name(dotted_name):
    """Resolve a dotted name to a real object
    """
    global _dotted_cache
    if dotted_name not in _dotted_cache:
        _dotted_cache[dotted_name] = resolve(dotted_name)
    return _dotted_cache[dotted_name]

def _get_disallowed_fields(context, permissions, prefix):
    """Get a list of fields for which the user does not have the requisite
    permission. 'permissions' is a dict with field names as keys and
    permission names as values. The permission names will be looked up
    as IPermission utilities.
    """
    
    security_manager = getSecurityManager()
    
    disallowed = []
    permission_cache = {} # name -> True/False
    
    for field_name, permission_name in permissions.items():
        if permission_name not in permission_cache:
            permission = queryUtility(IPermission, name=permission_name)
            if permission is None:
                permission_cache[permission_name] = True
            else:
                permission_cache[permission_name] = security_manager.checkPermission(permission.title, context)
        if not permission_cache[permission_name]:
            disallowed.append(_fn(prefix, field_name))
    
    return disallowed

# Some helper functions

def _fn(prefix, field_name):
    """Give prefixed fieldname if applicable
    """
    if prefix:
        return expandPrefix(prefix) + field_name
    else:
        return field_name

def _bn(field):
    """Give base (non-prefixed) fieldname
    """
    prefix = field.prefix
    field_name = field.__name__
    if prefix:
        return field_name[len(prefix) + 1:]
    else:
        return field_name

def _process_widgets(form, widgets, modes, new_fields):
    """Update the fields list with widgets
    """

    for field_name in new_fields:
        field = new_fields[field_name]
        base_name = _bn(field)
        
        widget_name = widgets.get(base_name, None)
        widget_mode = modes.get(base_name, field.mode) or form.mode or INPUT_MODE
        
        widget_factory = None
        if widget_name is not None:
            if isinstance(widget_name, basestring):
                widget_factory = resolve_dotted_name(widget_name)
            elif IFieldWidget.implementedBy(widget_name):
                widget_factory = widget_name
            
            if widget_factory is not None:
                field.widgetFactory[widget_mode] = widget_factory
        
        if base_name in modes:
            new_fields[field_name].mode = widget_mode

def process_fields(form, schema, prefix='', default_group=None, permission_checks=True):
    """Add the fields from the schema to the from, taking into account
    the hints in the various tagged values as well as fieldsets. If prefix
    is given, the fields will be prefixed with this prefix. If 
    default_group is given (as a Fieldset instance), any field not explicitly
    placed into a particular fieldset, will be added to the given group,
    which must exist already. If permission_checks is false,
    permission checks are ignored.
    """

    # Get data from tagged values, flattening data from super-interfaces
    
    # Note: The names always refer to a field in the schema, and never contain a prefix.
    
    omitted   = merged_tagged_value_dict(schema, OMITTED_KEY)   # name => e.g. 'true'
    modes     = merged_tagged_value_dict(schema, MODES_KEY)     # name => e.g. 'hidden'
    widgets   = merged_tagged_value_dict(schema, WIDGETS_KEY)   # name => widget/dotted name

    fieldsets = merged_tagged_value_list(schema, FIELDSETS_KEY) # list of IFieldset instances

    # Get either read or write permissions depending on what type of form this is

    permissions = {}
    if permission_checks:
        if form.mode == DISPLAY_MODE:
            permissions = merged_tagged_value_dict(schema, READ_PERMISSIONS_KEY)  # name => permission name
        elif form.mode == INPUT_MODE:
            permissions = merged_tagged_value_dict(schema, WRITE_PERMISSIONS_KEY) # name => permission name
    
    # Find the fields we should not worry about
    
    groups = {}
    do_not_process = list(form.fields.keys())
    do_not_process.extend(_get_disallowed_fields(form.context, permissions, prefix))

    for field_name, status in omitted.items():
        do_not_process.append(_fn(prefix, field_name))
    
    for group in form.groups:
        do_not_process.extend(list(group.fields.keys()))
        
        group_name = getattr(group, '__name__', group.label)
        groups[group_name] = group

    # Find all allowed fields so that we have something to select from
    all_fields = field.Fields(schema, prefix=prefix, omitReadOnly=True).omit(*do_not_process)
    
    # Keep track of which fields are in a fieldset, and, by elimination,
    # which ones are not 
    
    fieldset_fields = []
    for fieldset in fieldsets:
        for field_name in fieldset.fields:
            fieldset_fields.append(_fn(prefix, field_name))
    
    # Set up the default fields, widget factories and widget modes
    
    new_fields = all_fields.omit(*fieldset_fields)
    _process_widgets(form, widgets, modes, new_fields)
    
    if not default_group:
        form.fields += new_fields
    else:
        groups[default_group].fields += new_fields
    
    # Set up fields for fieldsets
    
    for fieldset in fieldsets:
        
        new_fields = all_fields.select(*[_fn(prefix, field_name) 
                                            for field_name in fieldset.fields
                                                if _fn(prefix, field_name) in all_fields])
        
        if len(new_fields) > 0:        
            _process_widgets(form, widgets, modes, new_fields)
        
            if fieldset.__name__ not in groups:
                form.groups.append(GroupFactory(fieldset.__name__,
                                                label=fieldset.label,
                                                description=fieldset.description,
                                                fields=new_fields))
            else:
                groups[fieldset.__name__].fields += new_fields
    
    
def process_field_moves(form, schema, prefix=''):
    """Process all field moves stored under ORDER_KEY in the schema tagged
    value. This should be run after all schemata have been processed with
    process_fields().
    """
    
    order = merged_tagged_value_list(schema, ORDER_KEY)      # (name, 'before'/'after', other name)
            
    for field_name, direction, relative_to in order:
        
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
                move(form, field_name, before=relative_to, prefix=prefix)
            elif direction == 'after':
                move(form, field_name, after=relative_to, prefix=prefix)
        except KeyError:
            # The relative_to field doesn't exist
            pass