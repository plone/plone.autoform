# -*- coding: utf-8 -*-
from collections import OrderedDict
from operator import attrgetter
from plone.autoform.interfaces import ORDER_KEY
from plone.autoform.utils import processFields
from plone.supermodel.interfaces import DEFAULT_ORDER
from plone.supermodel.utils import mergedTaggedValueList
from plone.z3cform.fieldsets.group import GroupFactory
from plone.z3cform.fieldsets.utils import move
from z3c.form import field
from z3c.form.util import expandPrefix

import logging


logger = logging.getLogger(__name__)
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

        for group in self.groups:
            group_name = getattr(group, '__name__', group.label)
            fieldset_group = GroupFactory(
                group_name,
                field.Fields(group.fields),
                group.label,
                getattr(group, 'description', None)
            )
            groups.append(fieldset_group)

        # Copy to instance variable only after we have potentially read from
        # the class
        self.groups = groups

        prefixes = {}

        if self.schema is not None:
            processFields(self, self.schema, permissionChecks=have_user)

        # Set up all widgets, modes, omitted fields and fieldsets
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
                # use interface name, or prefix for anonymous schema
                group_name = schema.__name__ or prefix or None

                # Look for group - note that previous processFields
                # may have changed the groups list, so we can't easily
                # store this in a dict.
                found = False
                for g in self.groups:
                    if group_name == getattr(g, '__name__', g.label):
                        found = True
                        break

                if not found:
                    fieldset_group = GroupFactory(
                        group_name,
                        field.Fields(),
                        label=group_name,
                        description=schema.__doc__,
                        order=DEFAULT_ORDER,
                    )
                    self.groups.append(fieldset_group)

                defaultGroup = group_name

            processFields(
                self,
                schema,
                prefix=prefix,
                defaultGroup=defaultGroup,
                permissionChecks=have_user
            )

        # Then process relative field movements. The base schema is processed
        # last to allow it to override any movements made in additional
        # schemata.
        rules = None
        for schema in self.additionalSchemata:
            order = mergedTaggedValueList(schema, ORDER_KEY)
            rules = self._calculate_field_moves(
                order,
                prefix=prefixes[schema],
                rules=rules,
            )
        if self.schema is not None:
            order = mergedTaggedValueList(self.schema, ORDER_KEY)
            rules = self._calculate_field_moves(order, rules=rules)
        self._cleanup_rules(rules)
        self._process_field_moves(rules)
        self._process_group_order()

    def getPrefix(self, schema):
        """Get the preferred prefix for the given schema
        """
        if self.ignorePrefix:
            return ''
        return schema.__name__

    def _prepare_names(self, source, target, prefix):
            # calculate prefixed fieldname
            if prefix:
                source = '{0}.{1}'.format(prefix, source)

            # Handle shortcut: leading . means "in this form". May be useful
            # if you want to move a field relative to one in the current
            # schema or (more likely) a base schema of the current schema,
            # without having to repeat the full prefix of this schema.
            if target.startswith('.'):
                target = target[1:]
                if prefix:
                    target = expandPrefix(prefix) + target
            return source, target

    def _cleanup_rules(self, rules):
        for rulename in rules['__all__']:
            if 'parent' in rules['__all__'][rulename]:
                del rules['__all__'][rulename]['parent']
        del rules['__all__']

    def _calculate_field_moves(self, order, prefix='', rules=None):
        """Calculates all needed field rules
        """
        # we want to be independent from the order of the schemas coming later
        # so a if field_c is first moved after field_a, then field_a is moved
        # after field_c, the output should be: b, a, c, because or first move
        # sticks
        if rules is None:
            rules = {}
        allrules = rules.get('__all__', None)
        if allrules is None:
            allrules = rules['__all__'] = dict()

        # (current field name, 'before'/'after', other field name)
        for source, direction, target in order:
            source, target = self._prepare_names(source, target, prefix)
            # use a simple tree to resolve dependencies
            rule = allrules.get(source, {})
            if (
                'target' in rule and target != rule['target']
            ):
                # target override
                # reset this rule to a stub first
                del rule['target']
                del rule['dir']
                rule['stub'] = True
                # unlink in parent
                del rule['parent']['with'][source]
                del rule['parent']
            if (
                'dir' in rule and direction != rule['dir']
            ):
                # direction override
                rule['dir'] = direction
            if not rule or rule.get('stub', False):
                if rule.get('stub', False):
                    del rule['stub']
                rule['target'] = target
                rule['dir'] = direction
                allrules[source] = rule

            # field is no longer a tree root
            if source in rules:
                del rules[source]

            target_rule = allrules.get(target, None)
            if target_rule is None:
                allrules[target] = target_rule = {
                    'stub': True,
                }
                rules[target] = target_rule
            if 'with' not in target_rule:
                target_rule['with'] = OrderedDict()
            rule['parent'] = target_rule
            target_rule['with'][source] = rule

        return rules

    def _process_field_moves(self, rules):
        """move fields according to the rules
        """
        for name, rule in rules.items():
            if name == '__all__':
                continue
            prefix = None
            if '.' in name:
                prefix, name = name.split('.', 1)
            else:
                prefix = ''
            if not rule.get('stub', False):
                after = rule['target'] if rule['dir'] == 'after' else None
                before = rule['target'] if rule['dir'] == 'before' else None
                if not (before or after):
                    raise ValueError(
                        'Direction of a field move must be before or '
                        'after, but got {0}.'.format(rule['direction'])
                    )
                try:
                    move(self, name, before=before, after=after, prefix=prefix)
                except KeyError:
                    # The relative_to field doesn't exist
                    logger.exception(
                        'No field move possible for non-existing field named '
                        '{0} with target {1}'.format(
                            prefix + '.' + name,
                            before or after
                        )
                    )
            self._process_field_moves(rule.get('with', {}))

    def _process_group_order(self):
        self.groups.sort(key=attrgetter('order'))
