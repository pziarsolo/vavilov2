from functools import reduce
import operator
from time import time

from django.db.models import Q
from django.views.generic.detail import DetailView

from django_tables2 import RequestConfig
from guardian.mixins import PermissionRequiredMixin

from vavilov.forms.accession import SearchPassportForm
from vavilov.models import (Accession, AccessionRelationship, Cvterm, Country,
                            Taxa, get_bottom_taxons)

from vavilov.views.tables import (ObservationsTable, AssaysTable, PlantsTable,
                                  AccessionsTable)
from vavilov.views.generic import SearchListView, calc_duration


def filter_accessions(search_criteria, user=None):
    query = Accession.objects
    if 'accession' in search_criteria:
        acc_code = search_criteria['accession']
        rels = AccessionRelationship.objects.filter(object__accession_number__icontains=acc_code)

        if rels:
            accs = [rel.subject for rel in rels]
            rel_query = reduce(operator.or_, [Q(accession_number=acc.accession_number) for acc in accs])
            query = query.filter(rel_query | Q(accessionsynonym__synonym_code__icontains=acc_code) |
                                 Q(accession_number__icontains=acc_code))
        else:
            query = query.filter(Q(accessionsynonym__synonym_code__icontains=acc_code) |
                                 Q(accession_number__icontains=acc_code))

    if 'collecting_source' in search_criteria and search_criteria['collecting_source']:
        col_source = Cvterm.objects.get(cvterm_id=search_criteria['collecting_source'])
        query = query.filter(passport__collecting_source=col_source)

    if 'country' in search_criteria and search_criteria['country']:
        country = Country.objects.get(country_id=search_criteria['country'])
        query = query.filter(passport__location__country=country)

    if 'region' in search_criteria and search_criteria['region']:
        region = search_criteria['region']
        query = query.filter(passport__location__region=region)

    if 'biological_status' in search_criteria and search_criteria['biological_status']:
        biological_status = Cvterm.objects.get(cvterm_id=search_criteria['biological_status'])
        query = query.filter(passport__biological_status=biological_status)

    if 'taxa_result' in search_criteria and search_criteria['taxa_result']:
        taxa = Taxa.objects.get(taxa_id=int(search_criteria['taxa_result']))
        bottom_taxas = get_bottom_taxons([taxa])
        query = query.filter(accessiontaxa__taxa__in=bottom_taxas)

    query = query.filter(type__name='internal')
    return query


class AccessionDetail(PermissionRequiredMixin, DetailView):
    model = Accession
    slug_url_kwarg = 'accession_number'
    slug_field = 'accession_number'
    permission_required = 'view_accession'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AccessionDetail, self).get_context_data(**kwargs)
        user = self.request.user
        # Add in a QuerySet of all the books
        # assays
        assays = self.object.assays(user)
        if assays:
            assay_table = AssaysTable(assays, template='table.html',
                                      prefix='assays-')
            RequestConfig(self.request).configure(assay_table)
        else:
            assay_table = None
        context['assays'] = assay_table

        # plants
        plants = self.object.plants(user)
        if plants:
            plant_table = PlantsTable(self.object.plants(user), template='table.html',
                                      prefix='plant-')
            RequestConfig(self.request).configure(plant_table)
        else:
            plant_table = None
        context['plants'] = plant_table

        # Observations
        prev_time = time()
        obs = self.object.observations(user)
        if obs:
            observations_table = ObservationsTable(obs, template='table.html',
                                                   prefix='observations-')
            prev_time = calc_duration('Table creation', prev_time)
            RequestConfig(self.request).configure(observations_table)
            prev_time = calc_duration('RequestConfig configure', prev_time)
        else:
            observations_table = None

        context['observations'] = observations_table

        context['obs_images'] = self.object.obs_images(user)
        # search_criteria
        context['obs_search_criteria'] = {'accession': self.object.accession_number}

        return context


class AccessionList(SearchListView):
    model = Accession
    template_name = 'vavilov/accession-list.html'
    form_class = SearchPassportForm
    table = AccessionsTable
    redirect_in_one = True
    detail_view_name = 'accession_view'

    def get_queryset(self, **kwargs):
        return filter_accessions(kwargs['search_criteria'],
                                      user=kwargs['user'])
