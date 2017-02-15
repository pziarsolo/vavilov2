from django import forms
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.db.models import Q
from vavilov_pedigree.models import Accession, Plant, SeedLot
from vavilov_pedigree.views.tables import (plant_to_table, seedlot_to_table,
                                           accession_to_table)


class SearchForm(forms.Form):
    anything = forms.CharField(label='Pedigree data', required=False)


class SearchView(FormView):
    template_name = 'vavilov_pedigree/search.html'
    form_class = SearchForm

    def get_success_url(self):
        return reverse('pedigree:search')

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        value = form.cleaned_data['anything']

        # do search
        plants = Plant.objects.filter(Q(plant_name__icontains=value) |
                                      Q(seed_lot__name__icontains=value))
        context['plants'] = plant_to_table(plants, self.request)

        seedlots = SeedLot.objects.filter(Q(name__icontains=value) |
                                          Q(accession__accession_number__icontains=value))
        context['seedlots'] = seedlot_to_table(seedlots, self.request)
        Accession.objects.all
        accessions = Accession.objects.filter(Q(accession_number__icontains=value) |
                                              Q(collecting_number__icontains=value))

        context['accessions'] = accession_to_table(accessions, self.request)

        return self.render_to_response(context)
