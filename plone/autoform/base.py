from z3c.form import field

from plone.z3cform.fieldsets.group import GroupFactory

from plone.autoform.utils import processFieldMoves, processFields

_marker = object()

class AutoFields(object):
    """Mixin class for the WidgetsView and AutoExtensibleForm classes.
    Takes care of actually processing field updates
    """

    schema = None
    additionalSchemata = ()
    
    fields = field.Fields()
    groups = ()
    
    ignorePrefix = False
    autoGroups = False
    
    def updateFieldsFromSchemata(self):
 
        # If the form is called from the ++widget++ traversal namespace,
        # we won't have a user yet. In this case, we can't perform permission
        # checks.
        
        have_user = bool(self.request.get('AUTHENTICATED_USER', False))
        
        # Turn fields into an instance variable, since we will be modifying it
        self.fields = field.Fields(self.fields)
        
        # Copy groups to an instance variable and ensure that we have
        # the more mutable factories, rather than 'Group' subclasses

        groups = []

        for g in self.groups:
            group_name = getattr(g, '__name__', g.label)
            fieldset_group = GroupFactory(group_name,
                                          field.Fields(g.fields),
                                          g.label,
                                          getattr(g, 'description', None))
            groups.append(fieldset_group)
        
        # Copy to instance variable only after we have potentially read from
        # the class
        self.groups = groups
        
        prefixes = {}
        
        # Set up all widgets, modes, omitted fields and fieldsets
        if self.schema is not None:
            processFields(self, self.schema, permissionChecks=have_user)
            for schema in self.additionalSchemata:
                
                # Find the prefix to use for this form and cache for next round
                prefix = self.getPrefix(schema)
                if prefix and prefix in prefixes:
                    prefix = schema.__identifier__
                prefixes[schema] = prefix
                
                # By default, there's no default group, i.e. fields go 
                # straight into the default fieldset
                
                defaultGroup = None
                
                # Create groups from schemata if requested and set default 
                # group

                if self.autoGroups:
                    group_name = schema.__name__
                    
                    # Look for group - note that previous processFields
                    # may have changed the groups list, so we can't easily
                    # store this in a dict.
                    found = False
                    for g in self.groups:
                        if group_name == getattr(g, '__name__', g.label):
                            found = True
                            break
                    
                    if not found:
                        fieldset_group = GroupFactory(group_name,
                                                      field.Fields(),
                                                      group_name,
                                                      schema.__doc__)
                        self.groups.append(fieldset_group)

                    defaultGroup = group_name
                    
                processFields(self, schema, prefix=prefix, defaultGroup=defaultGroup, permissionChecks=have_user)
        
        # Then process relative field movements. The base schema is processed
        # last to allow it to override any movements made in additional 
        # schemata.
        if self.schema is not None:
            for schema in self.additionalSchemata:
                processFieldMoves(self, schema, prefix=prefixes[schema])
            processFieldMoves(self, self.schema)
            
    def getPrefix(self, schema):
        """Get the preferred prefix for the given schema
        """
        if self.ignorePrefix:
            return ''
        return schema.__name__