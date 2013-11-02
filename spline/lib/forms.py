# encoding: utf8
"""Useful extra form fields."""

from sqlalchemy.orm.exc import NoResultFound
from wtforms import fields, widgets, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
try:
    from wtforms.fields.core import UnboundField
except ImportError:
    from wtforms.fields import UnboundField


class FakeMultiDict(dict):
    def getlist(self, key):
        return self[key]

class DuplicateField(fields.Field):
    """
    Wraps a field that must be rendered several times.  Similar to FieldList,
    except the fields are identical -- names are unchanged.

    Do NOT use this for multi-select fields, compound fields, or subforms!
    """
    widget = widgets.ListWidget()

    def __init__(self, unbound_field, label=None, validators=None, min_entries=0,
                 max_entries=None, default=[], **kwargs):
        super(DuplicateField, self).__init__(label, validators, default=default, **kwargs)
        if self.filters:
            raise TypeError('DuplicateField does not accept any filters. Instead, define them on the enclosed field.')
        if validators:
            raise TypeError('DuplicateField does not accept any validators. Instead, define them on the enclosed field.')
        assert isinstance(unbound_field, UnboundField), 'Field must be unbound, not a field class'

        self.unbound_field = unbound_field
        self.min_entries = min_entries
        self.max_entries = max_entries
        self._prefix = kwargs.get('_prefix', '')

    def process(self, formdata, data=fields._unset_value):
        if data is fields._unset_value or not data:
            try:
                data = self.default()
            except TypeError:
                data = self.default
        else:
            assert not self.max_entries or len(data) < self.max_entries, \
                'You cannot have more than max_entries entries in this DuplicateField'

        # Grab data from the incoming form
        if formdata:
            valuelist = formdata.getlist(self.name)
            if self.max_entries:
                valuelist = valuelist[0:self.max_entries]
        else:
            valuelist = []

        # Create the subfields
        self.entries = []
        self.data = []

        num_entries = max(self.min_entries, len(valuelist), len(data))
        subsubfields = []
        for i in range(num_entries):
            subfield = self.unbound_field.bind(form=None, prefix=self._prefix,
                                               name=self.short_name, id="{0}-{1}".format(self.id, i))

            if i == 0:
                if formdata and hasattr(subfield, 'subfield_names'):
                    subsubfields = list(subfield.subfield_names)

            # See if there's any form data to give the field
            fakedata = FakeMultiDict()
            if i < len(valuelist):
                fakedata[subfield.name] = [valuelist[i]]
            for name in subsubfields:
                subvaluelist = formdata.getlist(name)
                if i < len(subvaluelist):
                    fakedata[name] = [subvaluelist[i]]

            if i < len(data):
                subfield.process(fakedata, data[i])
            else:
                subfield.process(fakedata)

            if subfield.default or subfield.data != subfield.default:
                self.data.append(subfield.data)

            self.entries.append(subfield)

    def validate(self, form, extra_validators=[]):
        self.errors = []
        success = True
        for subfield in self.entries:
            if not subfield.validate(form):
                success = False
                self.errors.append(subfield.errors)
        return success

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, index):
        return self.entries[index]


class MultiCheckboxField(fields.SelectMultipleField):
    """ A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QueryRadioSelectField(QuerySelectField):
    """
    Works the same as a QuerySelectField, except using radio buttons
    rather than a selectbox.

    Iterating over the field yields the radio subfields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.RadioInput()

class QueryCheckboxSelectMultipleField(QuerySelectMultipleField):
    """
    Works the same as a QuerySelectMultipleField, except using checkboxes
    rather than a selectbox.

    Iterating over the field yields the checkbox subfields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QueryTextField(fields.TextField):
    """
    Represents a database object entered in a freeform text field.  Works
    similarly to `QuerySelectField`, but avoids the problem of scaling a
    drop-down field to a table with hundreds of rows or more.

    The following arguments are different from `QuerySelectField`:

     `query_factory` is still expected to return a query, but it takes a single
     argument: the incoming form value.

     `query_factory` is required; setting the `query` property of a field is
     not supported.

     If the input is valid, `get_label` is used to set the rendered textbox's
     value.  This may matter if your query performs a case-insensitive search,
     for example.

     `get_pk` is not required.
    """
    def __init__(self, label=None, validators=None, query_factory=None,
                 get_label=None, allow_blank=False, **kwargs):
        super(QueryTextField, self).__init__(label, validators, **kwargs)
        if not query_factory:
            raise Exception('A QueryTextField must have a query_factory.')

        self._original_value = u''
        self.query_factory = query_factory
        self.get_label = get_label
        self.allow_blank = allow_blank
        self.query = None

    def process_formdata(self, valuelist):
        """Processes and loads the form value."""
        self.data = None
        if valuelist:
            self._original_value = valuelist[0]

            if valuelist[0] == u'':
                return

            try:
                self.data = self.query_factory(valuelist[0]).one()
            except NoResultFound:
                raise ValidationError('Not a valid choice.')

    def _value(self):
        """Converts Python value back to a form value."""
        if self.data is None:
            return self._original_value
        elif self.get_label:
            return self.get_label(self.data)
        else:
            return unicode(self.data)

    def pre_validate(self, form):
        if not self.allow_blank and self._original_value == u'':
            raise ValidationError('This field is required.')
