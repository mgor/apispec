# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from functools import partial

from wtforms.validators import ValidationError as WTFValidationError
from wtforms.i18n import get_translations

from .core import BaseConverter, ValidationError

class DummyField(object):
    def __init__(self, data, errors=(), raw_data=None, _translations=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data
        self._translations = _translations

    def gettext(self, string):
        return self._translations.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._translations.ngettext(singular, plural, n)

dummy_form = dict()

class from_wtforms(BaseConverter):
    """Convert a WTForms validator from `wtforms.validators` to a marshmallow validator.

    Example::

        from marshmallow import fields
        from smore.validate.wtforms import from_wtforms
        from wtforms.validators import Length

        password = fields.Str(
            validate=from_wtforms([Length(min=8, max=100)])
        )

    :param list validators: WTForms validators.
    :param list locales: List of locales for error messages, in order. If `None`, will
        try to use locale information from the environment.
    """
    def __init__(self, validators, locales=None):
        BaseConverter.__init__(self, validators)
        self._translations = get_translations(locales)

    def make_validator(self, wtf_validator):
        def marshmallow_validator(value):
            field = DummyField(value, _translations=self._translations)
            field.data = value
            try:
                wtf_validator(dummy_form, field)
            except WTFValidationError as err:
                raise ValidationError(str(err))
        return marshmallow_validator

def make_converter(locales):
    return partial(from_wtforms, locales=locales)
