from zope.interface import implements
from zope.component import queryUtility

from zope.schema import getFieldsInOrder

from zope.security.interfaces import IPermission

from z3c.form import field
from z3c.form.util import expandPrefix
from z3c.form.interfaces import IFieldWidget, INPUT_MODE, DISPLAY_MODE

from plone.autoform.interfaces import IAutoExtensibleForm

from plone.autoform.utils import resolve_dotted_name

from plone.supermodel.utils import merged_tagged_value_dict
from plone.supermodel.utils import merged_tagged_value_list

from plone.z3cform.fieldsets.extensible import ExtensibleForm
from plone.z3cform.fieldsets.group import GroupFactory

from plone.z3cform.fieldsets.utils import move

from plone.supermodel.interfaces import FIELDSETS_KEY

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

from AccessControl import getSecurityManager

_marker = object()

def get_disallowed_fields(context, permissions):
    """Get a list of fields for which the user does not have the requisite
    permission. security is a dict with field names as keys. The value
    under each field name is another dict, with keys 'read-permission' and/or
    'write-permission', in turn containing the name of an IPermission utility.
    permission_type should be one of 'read-permission' or 'write-permission'.
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
            disallowed.append(field_name)
    
    return disallowed

def process_fields(form, schema, prefix=None):
    """Add the fields from the schema to the from, taking into account
    the hints in the various tagged values as well as fieldsets.
    """

    # Get data from tagged values, flattening data from super-interfaces
    
    # Note: The names always refer to a field in the schema, and never contain a prefix.
    
    omitted   = merged_tagged_value_dict(schema, OMITTED_KEY)   # name => e.g. 'true'
    modes     = merged_tagged_value_dict(schema, MODES_KEY)     # name => e.g. 'hidden'
    widgets   = merged_tagged_value_dict(schema, WIDGETS_KEY)   # name => widget/dotted name

    fieldsets = merged_tagged_value_list(schema, FIELDSETS_KEY) # list of IFieldset instances

    # Get either read or write permissions depending on what type of form this is

    permissions = {}
    if form.mode == DISPLAY_MODE:
        permissions = merged_tagged_value_dict(schema, READ_PERMISSIONS_KEY)  # name => permission name
    elif form.mode == INPUT_MODE:
        permissions = merged_tagged_value_dict(schema, WRITE_PERMISSIONS_KEY) # name => permission name

    # Some helper functions
    
    def _fn(field_name):
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
    
    def process_widgets(form, new_fields):
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
    
    # Keep track of the fields we've already processed (i.e. they're in
    # form.fields or in a group's fields list)
    
    already_processed = []
    if form.fields is not None:
        already_processed.extend(form.fields.keys())
    for group in form.groups:
        if group.fields is not None:
            already_processed.extend(group.fields.keys())
    
    # Keep track of groups
    
    groups = dict([(getattr(g, '__name__', g.label), g) for g in form.groups])

    disallowed_fields = get_disallowed_fields(form.context, permissions)

    # Find all allowed fields so that we have something to select from
    
    if prefix:
        all_fields = field.Fields(schema, prefix=prefix, omitReadOnly=True).omit(*disallowed_fields)
    else:
        all_fields = field.Fields(schema, omitReadOnly=True).omit(*disallowed_fields)
    
    # Keep track of which fields are in a fieldset, and, by elimination,
    # which ones are not 
    
    fieldset_fields = set()
    for fieldset in fieldsets:
        for field_name in fieldset.fields:
            fieldset_fields.add(field_name)
    
    default_fieldset_fields = [_fn(f) for f, value in getFieldsInOrder(schema) 
                                        if not value.readonly
                                            and f not in fieldset_fields
                                            and f not in disallowed_fields
                                            and not omitted.get(f, False)]
    
    # Set up the default fields, widget factories and widget modes
    
    new_fields = all_fields.select(*default_fieldset_fields)
    process_widgets(form, new_fields)
    
    if form.fields is None:
        form.fields = new_fields
    else:
        form.fields += new_fields.omit(*already_processed)
    
    # Set up fields for fieldsets
    
    for fieldset in fieldsets:
        
        new_fields = all_fields.select(*[_fn(field_name) for field_name in fieldset.fields])
        process_widgets(form, new_fields)
        
        if fieldset.__name__ not in groups:
            form.groups.append(GroupFactory(fieldset.__name__,
                                            label=fieldset.label,
                                            description=fieldset.description,
                                            fields=new_fields))
        else:
            groups[fieldset.__name__].fields += new_fields.omit(*already_processed)
    
    
def process_field_moves(form, schema, prefix=None):
    """Process all field moves stored under ORDER_KEY in the schema tagged
    value. This should be run after all schemata have been processed with
    process_fields().
    """
    
    order = merged_tagged_value_list(schema, ORDER_KEY)      # (name, 'before'/'after', other name)
    
    def _fn(field_name):
        """Give prefixed fieldname if applicable
        """
        if prefix:
            return expandPrefix(prefix) + field_name
        else:
            return field_name
        
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

class AutoExtensibleForm(ExtensibleForm):
    """Mixin class for z3c.form forms that support fields extracted from
    a schema
    """

    implements(IAutoExtensibleForm)
    
    fields = _marker
    groups = []
    
    @property
    def schema(self):
        raise NotImplemented("The class deriving from AutoExtensibleForm must have a 'schema' property")

    @property
    def additional_schemata(self):
        """Default to there being no additional schemata
        """
        return ()
    
    def updateFieldsFromSchemata(self):
        
        # First set up all widgets, modes, omitted fields and fieldsets
        process_fields(self, self.schema)
        for schema in self.additional_schemata:
            process_fields(self, schema, prefix=schema.__identifier__)
        
        # Then process relative field movements. The base schema is processed
        # last to allow it to override any movements made in additional 
        # schemata.
        for schema in self.additional_schemata:
            process_field_moves(self, schema, prefix=schema.__identifier__)
        process_field_moves(self, self.schema)
        
    def updateFields(self):
        
        # Keep an existing value if we've been subclassed and this has been
        # set to a real set of fields
        if self.fields is _marker:
            self.fields = None
        else:
            self.fields = field.Fields(self.fields)
        
        # Copy groups to an instance variable and ensure that we have
        # the more mutable factories, rather than 'Group' subclasses

        self.groups = [GroupFactory(getattr(g, '__name__', g.label),
                                    field.Fields(g.fields),
                                    g.label,
                                    getattr(g, 'description', None))
                        for g in self.groups]
        
        # Update fields from schemata
        
        self.updateFieldsFromSchemata()
        
        # Allow the regular adapters to update the fields
        super(AutoExtensibleForm, self).updateFields()
