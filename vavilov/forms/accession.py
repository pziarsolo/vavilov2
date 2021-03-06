from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Select

from vavilov.caches import get_passport_data_choices
from vavilov.conf.settings import ACCESSION_SEARCH_FIELDS
from vavilov.forms.widgets import AutocompleteTextInput
from vavilov.models import Accession


class AccessionField(forms.CharField):
    '''A specialized Field that validates the feature type given'''

    def to_python(self, value):
        'It transforms the value into a cvterm'

        if not value:
            return ''
        elif value.isdigit():
            return self._search_item_id(value, 'id')
        else:
            return self._search_item_id(value, 'accession_code')

    def _search_item_id(self, value, kind):
        'It returns the featureSrc given the name or id'
        try:
            if kind == 'id':
                accession = Accession.objects.get(accession_id=value)
            else:
                accession = Accession.objects.get(accession_number=value)
        except Accession.DoesNotExist:
            raise ValidationError('v does not exists: {}'.format(value))
        return str(accession.accession_id)


class SearchPassportForm(forms.Form):
    help_name = 'Accession name'
    accession = forms.CharField(max_length=100, required=False, label=help_name,
                                widget=AutocompleteTextInput(source='/apis/accession_numbers/',
                                                             min_length=1,
                                                             force_check=False))
    if 'taxa' in ACCESSION_SEARCH_FIELDS:
        help_name = 'Taxa'
        taxa = forms.CharField(max_length=200, required=False, label=help_name,
                               widget=AutocompleteTextInput(source='/apis/taxons/',
                                                            min_length=1,
                                                            force_check=True))
        taxa_result = forms.CharField(max_length=100, required=False,
                                      widget=forms.HiddenInput())

    passport_search_fields = ['country', 'region', 'biological_status',
                              'collecting_source']

    if 'country' in ACCESSION_SEARCH_FIELDS:
        country = forms.CharField(max_length=100, required=False,
                                  widget=Select(choices=[]))
    if 'region' in ACCESSION_SEARCH_FIELDS:
        region = forms.CharField(max_length=100, required=False,
                                 widget=Select(choices=[]))

    if 'biological_status' in ACCESSION_SEARCH_FIELDS:
        biological_status = forms.CharField(max_length=100, required=False,
                                            widget=Select(choices=[]))

    if 'collecting_source' in ACCESSION_SEARCH_FIELDS:
        collecting_source = forms.CharField(max_length=100, required=False,
                                            widget=Select(choices=[]))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass_choices = get_passport_data_choices()
        for field in ('country', 'region', 'biological_status', 'collecting_source'):
            if field in self.fields:
                self.fields[field].widget.choices = pass_choices[field]
