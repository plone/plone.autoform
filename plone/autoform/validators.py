import re
import z3c.form
import zope.component
import zope.interface

from plone.autoform.interfaces import IParameterizedValidatorFactory
from plone.autoform.interfaces import IParameterizedWidget
from plone.autoform.widgets import WidgetExportImportHandler


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


class IRegExParamValidator(IParameterizedWidget):
    """ test parameterized validator schema """

    ignore = zope.schema.TextLine(title=u"Ignore Expression", required=False)
    regex = zope.schema.TextLine(title=u"Match Expression")
    errmsg = zope.schema.TextLine(title=u"Error Message", required=False)
    ignore_case = zope.schema.Bool(
        title=u"Ignore Case",
        default=True,
        required=False)


@zope.interface.implementer(IRegExParamValidator)
class RegExValidator(object):
    def __init__(self, request):
        pass

RegExParamValidatorExportImportHandler = \
    WidgetExportImportHandler(IRegExParamValidator)
