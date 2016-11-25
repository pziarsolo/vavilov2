from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django_tables2 import RequestConfig
from django_tables2.utils import A
from guardian.shortcuts import get_objects_for_user

import django_tables2 as tables

from vavilov.forms.observations import SearchObservationForm
from vavilov.models import Observation, Plant
from vavilov.utils.streams import return_csv_response, return_excel_response


class ObservationsTable(tables.Table):
    Accession = tables.LinkColumn('accession_view', args=[A('accession.accession_number')],
                                  accessor=A('accession.accession_number'),
                                  orderable=True, verbose_name='Accession')
    plant = tables.LinkColumn('plant_view', args=[A('plant_part.plant.unique_id')],
                              accessor=A('plant_part.plant.unique_id'),
                              orderable=True, verbose_name='Plant')
    plant_part = tables.Column('Plant part', accessor=A('obs_entity.part.name'),
                               default='', orderable=True)
    assay = tables.LinkColumn('assay_view', args=[A('assay.name')],
                              accessor=A('assay.name'),
                              orderable=True, verbose_name='Assay')
    trait = tables.LinkColumn('trait_view', args=[A('trait.trait_id')],
                              accessor=A('trait.name'),
                              orderable=True, verbose_name='Trait')
    value = tables.Column('Value', accessor=A('value'),
                          default='', orderable=True)
    observer = tables.Column('Observer', accessor=A('observer'),
                             default='', orderable=True)
    creation_time = tables.Column('Creation Time',
                                  accessor=A('creation_time'),
                                  default='', orderable=True)

    class Meta:
        attrs = {"class": "searchresult"}


def _build_entry_query(search_criteria, user):
    query = Observation.objects.all()
    if 'accession' in search_criteria and search_criteria['accession'] != "":
        accession_code = search_criteria['accession']
        acc_plants = Plant.objects.filter(Q(accession__accession_number__icontains=accession_code) |
                                          Q(accession__accessionsynonyms__synonym_code__icontains=accession_code))
        query = query.filter(obs_entity__obsentityplant__plant__in=acc_plants)

#         query = query.filter(Q(plant_part__plant__accession__code__icontains=accession_code) |
#                              Q(plant_part__plant__accession__accessionsynonyms__code__icontains=accession_code))
    if 'plant' in search_criteria and search_criteria['plant'] != "":
        plant_code = search_criteria['plant']
        query = query.filter(plant_part__plant__unique_id__icontains=plant_code)

    if 'plant_part' in search_criteria and search_criteria['plant_part'] != "":
        plant_part = search_criteria['plant_part']
        query = query.filter(obs_entity__part__name=plant_part)

    if 'assay' in search_criteria and search_criteria['assay'] != "":
        query = query.filter(assay__name=search_criteria['assay'])

    if 'trait' in search_criteria and search_criteria['trait']:
        trait_id = search_criteria['trait']
        query = query.filter(trait=trait_id)

    if 'experimental_field' in search_criteria and search_criteria['experimental_field']:
        query = query.filter(plant__experimental_field__icontains=search_criteria['experimental_field'])

    if 'observer' in search_criteria and search_criteria['observer']:
        observer = search_criteria['observer']
        query = query.filter(user__icontains=observer)
    query = get_objects_for_user(user, 'vavilov.view_observation',
                                 klass=query)

    return query


@login_required
def search(request):
    context = RequestContext(request)
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

    template = 'search_observations.html'

    if request_data:
        form = SearchObservationForm(request_data)
        if form.is_valid():
            search_criteria = form.cleaned_data
            search_criteria = dict([(key, value) for key, value in
                                    search_criteria.items() if value])
            context['search_criteria'] = search_criteria

            queryset = _build_entry_query(search_criteria, user=request.user)
            download_search = request.GET.get('download_search', False)

            if download_search:
                format_ = request.GET['format']
                if format_ == 'csv':
                    return return_csv_response(queryset, ObservationsTable)
                elif format_ == 'excel':
                    return return_excel_response(queryset, ObservationsTable)

            elif queryset and not download_search:
                entries_table = ObservationsTable(queryset,
                                                  template='table.html')
                RequestConfig(request).configure(entries_table)
                context['entries'] = entries_table
                # we only have to write the criteria in the form the first
                if not getdata:
                    context['criteria'] = ''.join(["&{}={}".format(k, v)
                                                  for k, v in search_criteria.items()])
            else:
                context['entries'] = None
    else:
        form = SearchObservationForm()

    context['form'] = form
    return render_to_response(template, context, content_type=content_type)
