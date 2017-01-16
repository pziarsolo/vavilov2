from django.db.models import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django_tables2 import RequestConfig

from guardian.decorators import permission_required
from guardian.shortcuts import get_objects_for_user


from vavilov.forms.observations import SearchObservationForm
from vavilov.models import Observation, Plant, ObservationEntity, ObservationImages, \
    Trait
from vavilov.utils.streams import return_csv_response, return_excel_response
from vavilov.views.tables import ObservationsTable, PlantsTable


def _build_entry_query(search_criteria, user):
    query = Observation.objects.all()
    if 'accession' in search_criteria and search_criteria['accession'] != "":
        accession_code = search_criteria['accession']
        acc_plants = Plant.objects.filter(Q(accession__accession_number__icontains=accession_code) |
                                          Q(accession__accessionsynonym__synonym_code__icontains=accession_code))

        query = query.filter(obs_entity__observationentityplant__plant__in=acc_plants)

    if 'plant' in search_criteria and search_criteria['plant'] != "":
        plant_code = search_criteria['plant']
        query = query.filter(plant_part__plant__unique_id__icontains=plant_code)

    if 'plant_part' in search_criteria and search_criteria['plant_part'] != "":
        plant_part = search_criteria['plant_part']
        query = query.filter(obs_entity__part__name=plant_part)

    if 'assay' in search_criteria and search_criteria['assay'] != "":
        query = query.filter(assay__name=search_criteria['assay'])

    if 'traits' in search_criteria and search_criteria['traits']:
        trait_ids = search_criteria['traits']
        trait_names = [t.strip() for t in trait_ids.split(',') if t]
        traits = Trait.objects.filter(name__in=trait_names)
        query = query.filter(trait__in=traits)

    if 'experimental_field' in search_criteria and search_criteria['experimental_field']:
        query = query.filter(plant__experimental_field__icontains=search_criteria['experimental_field'])

    if 'observer' in search_criteria and search_criteria['observer']:
        observer = search_criteria['observer']
        query = query.filter(user__icontains=observer)

    query = get_objects_for_user(user, 'vavilov.view_observation', klass=query)

    photoqueryset = ObservationImages.objects.filter(observation__in=query)
    photoqueryset = get_objects_for_user(user,
                                         'vavilov.view_observation_images',
                                         klass=photoqueryset)
    obs = [po.observation.observation_id for po in photoqueryset]
    query = query.exclude(observation_id__in=obs)
    return query, photoqueryset


def _search_criteria_to_get_parameters(search_criteria):
    get_params = ''
    for key, value in search_criteria.items():
        if isinstance(value, list):
            for val in value:
                get_params += "&{}={}".format(key, val)
        else:
            get_params += "&{}={}".format(key, value)
    return get_params


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

    template = 'vavilov/search_observations.html'

    if request_data:
        form = SearchObservationForm(request_data)
        if form.is_valid():
            search_criteria = form.cleaned_data
            search_criteria = dict([(key, value) for key, value in
                                    search_criteria.items() if value])
            context['search_criteria'] = search_criteria

            queryset, photoqueryset = _build_entry_query(search_criteria,
                                                         user=request.user)

            download_search = request.GET.get('download_search', False)

            if download_search:
                format_ = request.GET['format']
                if format_ == 'csv':
                    return return_csv_response(queryset, ObservationsTable)
                elif format_ == 'excel':
                    return return_excel_response(queryset, ObservationsTable)

            elif (queryset or photoqueryset) and not download_search:
                if queryset:
                    entries_table = ObservationsTable(queryset,
                                                      template='table.html')
                    RequestConfig(request).configure(entries_table)
                    context['entries'] = entries_table
                else:
                    context['entries'] = None
                if photoqueryset:
                    context['photo_entries'] = photoqueryset
                else:
                    context['photo_entries'] = None
                # we only have to write the criteria in the form the first
                if not getdata:
                    context['criteria'] = _search_criteria_to_get_parameters(search_criteria)
            else:
                context['entries'] = None
    else:
        form = SearchObservationForm()

    context['form'] = form
    return render_to_response(template, context, content_type=content_type)


@permission_required('view_obs_entity', (ObservationEntity, 'name',
                                         'name'))
def observation_entity(request, name):
    user = request.user
    context = RequestContext(request)
    try:
        obs_entity = ObservationEntity.objects.get(name=name)
    except ObservationEntity.DoesNotExist:
        obs_entity = None
    context['obs_entity'] = obs_entity

    if obs_entity:
        plants = obs_entity.plants(user)
        if plants:
            plant_table = PlantsTable(plants, template='table.html',
                                      prefix='plant-')
            RequestConfig(request).configure(plant_table)
        else:
            plant_table = None
        context['plants'] = plant_table

        obs = obs_entity.observations(user)
        if obs:
            observations_table = ObservationsTable(obs, template='table.html',
                                                   prefix='observations-')
            RequestConfig(request).configure(observations_table)
        else:
            observations_table = None

        context['observations'] = observations_table
        context['obs_images'] = obs_entity.obs_images(user)

    template = 'vavilov/obs_entity.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)
