from django import forms
from django.forms.widgets import Select

from vavilov.forms.widgets import (AutocompleteTextInput,
                                   AutocompleteTextMultiInput)
from vavilov.models import Trait, Assay, Cvterm, Accession, TraitProp
from vavilov.conf.settings import OBSERVATIONS_HAVE_TIME, OBSERVATION_SEARCH_FIELDS


def grouped_trait_choices():
    trait_choices = []
    for trait in Trait.objects.all():
        trait_choices.append((trait.trait_id, trait.name))
    return trait_choices


class SearchObservationForm(forms.Form):
    if 'accession_number' in OBSERVATION_SEARCH_FIELDS:
        widget = AutocompleteTextInput(source='/apis/accession_numbers/', min_length=1,
                                       force_check=False)
        accession = forms.CharField(max_length=100, required=False,
                                    label='Accession and synonyms', widget=widget)
    if 'accession_list' in OBSERVATION_SEARCH_FIELDS:
        acc_list = forms.CharField(max_length=10000, required=False,
                                   label='List of accessions(one per line)', widget=forms.Textarea())
    if 'plant' in OBSERVATION_SEARCH_FIELDS:
        widget = AutocompleteTextInput(source='/apis/plants/', min_length=1,
                                       force_check=False)
        plant = forms.CharField(max_length=100, required=False,
                                label='Plant', widget=widget)
    if 'plant_part' in OBSERVATION_SEARCH_FIELDS:
        plant_part = forms.CharField(label='Plant part', required=False,
                                     widget=Select(choices=[]))
    if 'assay' in OBSERVATION_SEARCH_FIELDS:
        assay = forms.CharField(label='Assay', required=False,
                                widget=Select(choices=[]))
    if 'trait' in OBSERVATION_SEARCH_FIELDS:
        traits = forms.CharField(max_length=100, required=False, label='Trait',
                                 widget=AutocompleteTextMultiInput(source='/apis/traits/',
                                                                   min_length=1,
                                                                   force_check=False))
    if 'type_tr' in OBSERVATION_SEARCH_FIELDS:
        tr_trait_type = forms.CharField(label='Traiditom data type ', required=False,
                                        widget=Select(choices=[]))
    if 'experimental_field' in OBSERVATION_SEARCH_FIELDS:
        experimental_field = forms.CharField(required=False,
                                             label='Experimental field')
    if OBSERVATIONS_HAVE_TIME:
        all_label = 'Check this if you just last values, not all data'
        only_last_data = forms.BooleanField(required=False, label=all_label)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assay_choices = [('', '')]
        assay_choices.extend([(assay.name, assay.name) for assay in Assay.objects.distinct()])
        self.fields['assay'].widget.choices = assay_choices

        plan_part_choices = [('', '')]
        for plant_part in Cvterm.objects.filter(cv__name='plant_parts'):
            part_type = plant_part.name
            plan_part_choices.append((part_type, part_type))
        self.fields['plant_part'].widget.choices = plan_part_choices

        if 'type_tr' in OBSERVATION_SEARCH_FIELDS:
            traditom_trait_type_choices = [('', '')]
            tr_types = set()
            for tr_type in TraitProp.objects.filter(type__name='type_tr'):
                type_name = tr_type.value
                tr_types.add(type_name)
            for tr_type in tr_types:
                traditom_trait_type_choices.append((tr_type, tr_type))
            self.fields['tr_trait_type'].widget.choices = traditom_trait_type_choices

    def clean_acc_list(self):
        acc_list_text = self.cleaned_data['acc_list']
        accessions_numbers = [acc.strip() for acc in acc_list_text.split('\n')]
        accs = []
        for accession_number in accessions_numbers:
            try:
                acc = Accession.objects.get(accession_number=accession_number)
                accs.append(acc)
            except Accession.DoesNotExist:
                pass
        return accs
