"""
This module contains a parameterized regular-expression
validator that may be used as a model for other
parameterized validators meant to be available via
supermodel XML.

Parameterized validators need 4 parts::

1) A factory function that accepts a parameter dictionary
   and returns a SimpleFieldValidator class. One way to do this
   with a class closure around the parameters.

2) That factory must be configured as a named utility providing
   IParameterizedValidatorFactory and having the dotted name
   we wish to use to access the validator.

3) The parameters for the validator must be specified in a
   schema class derived from IParameterizedWidget. A class
   that implements this must be supplied with a name that
   in dotted format matches the factory utility's name.

4) A named utility implementing IWidgetExportImportHandler must
   be supplied. The name should be the same as for the validator
   factory and the parameterized widget utility.

This scheme allows our supermodel parser to take a dotted name
and find an export/import handler for the parameters. That
allows us to read the parameters from XML.

With the parameters, we can use the same dotted name to find
a factory for our validator class, which will get at the
parameters via closure.
"""

import re
import z3c.form
import zope.component
import zope.interface

from plone.autoform.interfaces import IParameterizedValidatorFactory
from plone.autoform.interfaces import IParameterizedWidget
from plone.autoform.widgets import WidgetExportImportHandler


# Implement a parameterized regular-expression validator

# This factory returns an class descended from IValidator
# with a closure around a parameter dictionary.
# This will be registered via zcml as a utility with
# the same dotted name as our our parameter widget class.
@zope.interface.implementer(IParameterizedValidatorFactory)
def regExValidatorFactory(params):

    class RegExValidator(z3c.form.validator.SimpleFieldValidator):

        def validate(self, value):
            super(RegExValidator, self).validate(value)
            errmsg = params.get('errmsg', u"Invalid input")
            ignore_case = params.get('ignore_case', True)
            options = 0
            if ignore_case:
                options = re.IGNORECASE
            ignore = re.compile(params.get('ignore', u''), options)
            regex = re.compile(params.get('regex', u".+"), options)
            if ignore:
                tvalue = ignore.sub(u'', value)
            else:
                tvalue = value
            if not regex.match(tvalue):
                # XXX Need a message factory
                raise zope.interface.Invalid(errmsg)

    return RegExValidator


# Schema for the parameters for our validator
class IRegExParamValidator(IParameterizedWidget):
    """ test parameterized validator schema """

    ignore = zope.schema.TextLine(title=u"Ignore Expression", required=False)
    regex = zope.schema.TextLine(title=u"Match Expression")
    errmsg = zope.schema.TextLine(title=u"Error Message", required=False)
    ignore_case = zope.schema.Bool(
        title=u"Ignore Case",
        default=True,
        required=False)


# We need a class that implements the schema interface and will
# have the same dotted name under which we'll register our
# two utilities.
@zope.interface.implementer(IRegExParamValidator)
class RegExValidator(object):
    def __init__(self, request):
        pass

# And, we'll need to be able to read the custom parameters. Do
# so by creating an ex/im handler and registering in ZCML
# as a utility with the same dotted name.
RegExParamValidatorExportImportHandler = \
    WidgetExportImportHandler(IRegExParamValidator)
