from operator import itemgetter

from django import forms
from django.forms.widgets import Select

from vavilov.forms.widgets import (AutocompleteTextInput,
                                   AutocompleteTextMultiInput)
from vavilov.models import Trait, Assay, Cvterm, Accession
from vavilov.conf.settings import OBSERVATIONS_HAVE_TIME


def grouped_trait_choices_old():
    traits_by_assay = {}
    for trait in Trait.objects.all():
        assay = trait.assay.name
        if assay not in traits_by_assay:
            traits_by_assay[assay] = []
        traits_by_assay[assay].append((trait.trait_id, trait.name))

    trait_choices = []
    for assay in sorted(traits_by_assay.keys()):
        traits = traits_by_assay[assay]
        trait_choices.append((assay, sorted(traits, key=itemgetter(1))))
    return trait_choices


def grouped_trait_choices():
    trait_choices = []
    for trait in Trait.objects.all():
        trait_choices.append((trait.trait_id, trait.name))
    return trait_choices


class SearchObservationForm(forms.Form):
    widget = AutocompleteTextInput(source='/apis/accession_numbers/', min_length=1,
                                   force_check=False)
    accession = forms.CharField(max_length=100, required=False,
                                label='Accession and synonyms', widget=widget)

    acc_list = forms.CharField(max_length=10000, required=False,
                               label='List of accessions(one per line)', widget=forms.Textarea())

    widget = AutocompleteTextInput(source='/apis/plants/', min_length=1,
                                   force_check=False)
    plant = forms.CharField(max_length=100, required=False,
                            label='Plant', widget=widget)
    plan_part_choices = [('', '')]
    for plant_part in Cvterm.objects.filter(cv__name='plant_parts'):
        part_type = plant_part.name
        plan_part_choices.append((part_type, part_type))

    plant_part = forms.CharField(label='Plan part', required=False,
                                 widget=Select(choices=plan_part_choices))
    assay_choices = [('', '')]
    assays = set([assay['name'] for assay in Assay.objects.all().values('name')])
    assay_choices.extend([(assay, assay) for assay in assays if assay is not None])
    assay = forms.ChoiceField(required=False, label='assay', widget=Select,
                              choices=assay_choices)

    traits = forms.CharField(max_length=100, required=False, label='Trait',
                             widget=AutocompleteTextMultiInput(source='/apis/traits/',
                                                               min_length=1,
                                                               force_check=False))

    experimental_field = forms.CharField(required=False,
                                         label='Experimental field')
    if OBSERVATIONS_HAVE_TIME:
        all_label = 'Check this if you want all data, not just last value'
        all_data = forms.BooleanField(required=False, label=all_label)


    def clean_acc_list(self):
        acc_list_text = self.cleaned_data['acc_list']
        accessions_numbers = [acc.strip() for acc in  acc_list_text.split('\n')]
        accs = []
        for accession_number in accessions_numbers:
            try:
                acc = Accession.objects.get(accession_number=accession_number)
                accs.append(acc)
            except Accession.DoesNotExist:
                pass
        return accs
