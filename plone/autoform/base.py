from z3c.form import field

from plone.z3cform.fieldsets.group import GroupFactory

from plone.autoform.utils import process_field_moves, process_fields

_marker = object()

class AutoFields(object):
    """Mixin class for the WidgetsView and AutoExtensibleForm classes.
    Takes care of actually processing field updates
    """
    
    fields = _marker
    groups = []
    
    def updateFieldsFromSchemata(self):

        # Keep an existing value if we've been subclassed and this has been
        # set to a real set of fields
        if self.fields is _marker:
            self.fields = None
        else:
            self.fields = field.Fields(self.fields)
        
        # Better to have an empty set of fields than None
        if self.fields is None and self.schema is None:
            self.fields = field.Fields()
        
        # Copy groups to an instance variable and ensure that we have
        # the more mutable factories, rather than 'Group' subclasses

        self.groups = [GroupFactory(getattr(g, '__name__', g.label),
                                    field.Fields(g.fields),
                                    g.label,
                                    getattr(g, 'description', None))
                        for g in self.groups]
        
        used_prefixes = set()
        prefixes = {}
        
        # Set up all widgets, modes, omitted fields and fieldsets        
        if self.schema is not None:
            process_fields(self, self.schema)
            for schema in self.additional_schemata:
                
                prefix = schema.__name__
                if prefix in used_prefixes:
                    prefix = schema.__identifier__
                used_prefixes.add(prefix)
                prefixes[schema] = prefix
                
                process_fields(self, schema, prefix=schema.__name__)
        
        # Then process relative field movements. The base schema is processed
        # last to allow it to override any movements made in additional 
        # schemata.
        for schema in self.additional_schemata:
            process_field_moves(self, schema, prefix=prefixes[schema])
        if self.schema is not None:
            process_field_moves(self, self.schema)