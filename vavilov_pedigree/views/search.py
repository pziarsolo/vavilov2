from django import forms
from django.db.models import Q
from vavilov_pedigree.models import (Accession, Plant, SeedLot,
                                     CrossExperimentSeedLot,
                                     filter_cross_experiments)
from vavilov_pedigree.views.tables import (plant_to_table, seedlot_to_table,
                                           accession_to_table, CrossTable)
from vavilov.views.generic import (search_criteria_to_get_parameters,
                                   SearchListView)
from django.template.context_processors import csrf
from django.shortcuts import render_to_response


class SearchForm(forms.Form):
    anything = forms.CharField(label='Pedigree data', required=False)


def search(request):
    context = {'request': request}
    context['user'] = request.user
    context.update(csrf(request))
    content_type = None  # default
    getdata = False

    if request.method == 'POST':
        request_data = request.POST
    elif request.method == 'GET':
        request_data = request.GET
        getdata = True
    else:
        request_data = None
    template = 'vavilov_pedigree/search.html'
    if request_data:
        form = SearchForm(request_data)
        if form.is_valid():
            search_criteria = form.cleaned_data
            search_criteria = dict([(key, value) for key, value in
                                    search_criteria.items() if value])
            context['search_criteria'] = search_criteria
            value = form.cleaned_data['anything']

            # do search
            plants = Plant.objects.filter(Q(plant_name__icontains=value) |
                                          Q(seed_lot__name__icontains=value))
            context['plants'] = plant_to_table(plants, request)

            seedlots = SeedLot.objects.filter(Q(name__icontains=value) |
                                              Q(accession__accession_number__icontains=value))
            context['seedlots'] = seedlot_to_table(seedlots, request)
            Accession.objects.all
            accessions = Accession.objects.filter(Q(accession_number__icontains=value) |
                                                  Q(collecting_number__icontains=value))

            context['accessions'] = accession_to_table(accessions, request)
            if not getdata:
                context['criteria'] = search_criteria_to_get_parameters(search_criteria)
    else:
        form = SearchForm()

    context['form'] = form
    return render_to_response(template, context, content_type=content_type)


class SearchCrossForm(forms.Form):
    description = forms.CharField(required=False,)
    father = forms.CharField(required=False, label='Father plant code or accession')
    mother = forms.CharField(required=False, label='Mother plant code or accession')
    offspring = forms.CharField(required=False, label='Offspring seedlot code or accession')


class CrossExperiments(SearchListView):
    model = CrossExperimentSeedLot
    template_name = 'vavilov_pedigree/cross_exp_list.html'
    form_class = SearchCrossForm
    table = CrossTable
    redirect_in_one = False
    detail_view_name = ''

    def get_queryset(self, **kwargs):
        search_criteria = kwargs['search_criteria']
        return filter_cross_experiments(search_criteria)

