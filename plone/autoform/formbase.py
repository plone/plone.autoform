from zope.interface import implements
from zope.schema import getFieldsInOrder

from z3c.form import field
from z3c.form.util import expandPrefix
from z3c.form.interfaces import INPUT_MODE, IFieldWidget

from plone.autoform.interfaces import IAutoExtensibleForm

from plone.autoform.utils import resolve_dotted_name
from plone.autoform.utils import merged_tagged_value_dict
from plone.autoform.utils import merged_tagged_value_list

from plone.z3cform.fieldsets.extensible import ExtensibleForm
from plone.z3cform.fieldsets.group import GroupFactory

from plone.z3cform.fieldsets.utils import move

from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.autoform.interfaces import FORMDATA_KEY

_marker = object()

def process_fields(form, schema, prefix=None):
    """Add the fields from the schema to the from, taking into account
    the hints in the FORMDATA_KEY tagged value as well as fieldsets.
    """
    
    def _fn(field_name):
        if prefix:
            return expandPrefix(prefix) + field_name
        else:
            return field_name
    
    form_data = merged_tagged_value_dict(schema, FORMDATA_KEY)
    fieldsets = merged_tagged_value_list(schema, FIELDSETS_KEY)
    
    # Get metadata
    
    omitted = frozenset([_fn(field_name) 
                    for field_name, value in form_data.get('omitted', []) if value])
    modes = dict([(_fn(field_name), value)
                    for field_name, value in form_data.get('modes', [])])
    widgets = dict([(_fn(field_name), value)
                    for field_name, value in form_data.get('widgets', [])])
    
    # Not a dict, since order matters!
    moves = [(_fn(field_name), value) for field_name, value in form_data.get('moves', [])]
    
    already_processed = []
    if form.fields is not None:
        already_processed.extend(form.fields.keys())
    for group in form.groups:
        if group.fields is not None:
            already_processed.extend(group.fields.keys())
    
    fieldset_fields = set()
    for fieldset in fieldsets:
        for field_name in fieldset.fields:
            fieldset_fields.add(_fn(field_name))
    
    default_fieldset_fields = [_fn(f) for f, value in getFieldsInOrder(schema) 
                                if not value.readonly and 
                                    _fn(f) not in fieldset_fields and 
                                    _fn(f) not in omitted]

    groups = dict([(getattr(g, '__name__', g.label), g) for g in form.groups])
    
    if prefix:
        all_fields = field.Fields(schema, prefix=prefix, omitReadOnly=True)
    else:
        all_fields = field.Fields(schema, omitReadOnly=True)
    
    # Set up the default fields, widget factories and widget modes
    
    new_fields = all_fields.select(*default_fieldset_fields)
    
    def process_widgets(new_fields):
        for field_name in new_fields:
            widget_name = widgets.get(field_name, None)
            widget_factory = None
            if widget_name is not None:
                if isinstance(widget_name, basestring):
                    widget_factory = resolve_dotted_name(widget_name)
                elif IFieldWidget.implementedBy(widget_name):
                    widget_factory = widget_name
                if widget_factory is not None:
                    new_fields[field_name].widgetFactory[modes.get(field_name, INPUT_MODE)] = widget_factory
            if field_name in modes:
                new_fields[field_name].mode = modes[field_name]
    
    process_widgets(new_fields)
    
    if form.fields is None:
        form.fields = new_fields
    else:
        form.fields += new_fields.omit(*already_processed)
    
    # Set up fields for fieldsets
    
    for fieldset in fieldsets:
        
        new_fields = all_fields.select(*[_fn(field_name) for field_name in fieldset.fields])
        process_widgets(new_fields)
        
        if fieldset.__name__ not in groups:
            form.groups.append(GroupFactory(fieldset.__name__,
                                            label=fieldset.label,
                                            description=fieldset.description,
                                            fields=new_fields))
        else:
            groups[fieldset.__name__].fields += new_fields.omit(*already_processed)
    
    # Process moves
    for field_name, before in moves:
        try:
            move(form, field_name, before=before)
        except KeyError:
            # The 'before' field doesn't exist
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
        process_fields(self, self.schema)
        for schema in self.additional_schemata:
            process_fields(self, schema, prefix=schema.__identifier__)
        
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
