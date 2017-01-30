from functools import reduce
import operator

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http.response import HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django_tables2 import RequestConfig
from guardian.decorators import permission_required

from vavilov.forms.accession import SearchPassportForm
from vavilov.models import (Accession, AccessionRelationship, Cvterm, Country,
                            Taxa, get_bottom_taxons)
from vavilov.utils.csv import return_csv_response
from vavilov.utils.streams import return_excel_response
from vavilov.views.tables import (ObservationsTable, AssaysTable, PlantsTable,
                                  AccessionsTable)


@permission_required('view_accession', (Accession, 'accession_number',
                                        'accession_number'))
def accession(request, accession_number):
    user = request.user
    context = RequestContext(request)
    try:
        acc = Accession.objects.get(accession_number=accession_number)
    except Accession.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    if acc.type.name == 'external':
        return HttpResponseNotFound('<h1>Page not found</h1>')

    context['accession'] = acc

    # assays
    assays = acc.assays(user)
    if assays:
        assay_table = AssaysTable(assays, template='table.html',
                                  prefix='assays-')
        RequestConfig(request).configure(assay_table)
    else:
        assay_table = None
    context['assays'] = assay_table

    # plants
    plants = acc.plants(user)
    if plants:
        plant_table = PlantsTable(acc.plants(user), template='table.html',
                                  prefix='plant-')
        RequestConfig(request).configure(plant_table)
    else:
        plant_table = None
    context['plants'] = plant_table

    # Observations
    obs = acc.observations(user)
    if obs:
        observations_table = ObservationsTable(obs, template='table.html',
                                               prefix='observations-')
        RequestConfig(request).configure(observations_table)
    else:
        observations_table = None

    context['observations'] = observations_table

    context['obs_images'] = acc.obs_images(user)
    # search_criteria
    context['obs_search_criteria'] = {'accession': acc.accession_number}

    template = 'vavilov/accession.html'
    return render_to_response(template, context)


def _build_accession_query(search_criteria, user=None):
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


def search(request):
    context = RequestContext(request)
    context.update(csrf(request))

    getdata = False
    if request.method == 'POST':
        request_data = request.POST
    elif request.method == 'GET':
        request_data = request.GET
        getdata = True
    else:
        request_data = None

    template = 'vavilov/search_accession.html'
    content_type = None  # default
    if request_data:
        form = SearchPassportForm(request_data)
        if form.is_valid():
            search_criteria = form.cleaned_data
            search_criteria = dict([(key, value) for key, value in
                                    search_criteria.items() if value])
            context['search_criteria'] = search_criteria
            queryset = _build_accession_query(search_criteria,
                                              user=request.user)
            download_search = request.GET.get('download_search', False)
            if download_search:
                format_ = request.GET['format']
                if format_ == 'csv':
                    return return_csv_response(queryset, AccessionsTable)
                elif format_ == 'excel':
                    return return_excel_response(queryset, AccessionsTable)

            elif queryset and not download_search:
                if len(queryset) == 1:
                    return redirect(reverse('accession_view',
                                            kwargs={'accession_number': queryset[0].accession_number}))

                accession_table = AccessionsTable(queryset,
                                                  template='table.html')
                RequestConfig(request).configure(accession_table)

                context['accessions'] = accession_table
                # we only have to write the criteria in the form the first
                # time we search
                if not getdata:
                    context['criteria'] = ''.join([";{}={}".format(k, v)
                                                   for k, v in search_criteria.items()])
            else:
                context['accessions'] = None
    else:
        form = SearchPassportForm()

    context['form'] = form
    return render_to_response(template, context, content_type=content_type)
