import logging

from time import time
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django_tables2 import RequestConfig

from guardian.decorators import permission_required

from vavilov.forms.observations import SearchObservationForm
from vavilov.models import ObservationEntity, filter_observations
from vavilov.utils.streams import return_csv_response, return_excel_response
from vavilov.views.tables import ObservationsTable, PlantsTable
from vavilov.conf.settings import MAX_PHOTO_IN_GALLERY, APP_LOGGER


logger = logging.getLogger(APP_LOGGER)

def _search_criteria_to_get_parameters(search_criteria):
    get_params = ''
    for key, value in search_criteria.items():
        if isinstance(value, list):
            for val in value:
                get_params += "&{}={}".format(key, val)
        else:
            get_params += "&{}={}".format(key, value)
    return get_params


def calc_duration(action, prev_time):
    now = time()
    logger.info('{}: Took {} secs'.format(action, round(now - prev_time, 2)))
    return now


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
            prev_time = time()
            queryset = filter_observations(search_criteria, user=request.user)
            prev_time = calc_duration('Obs query', prev_time)

            photoqueryset = filter_observations(search_criteria, user=request.user,
                                                images=True)
            prev_time = calc_duration('Photo query', prev_time)

            have_obs = True if queryset.exists() else False
            prev_time = calc_duration('Check query', prev_time)

            num_photos = photoqueryset.count()
            prev_time = calc_duration('Count photos', prev_time)

            download_search = request.GET.get('download_search', False)

            if download_search:
                format_ = request.GET['format']
                if format_ == 'csv':
                    return return_csv_response(queryset, ObservationsTable)
                elif format_ == 'excel':
                    return return_excel_response(queryset, ObservationsTable)

            elif (have_obs or num_photos > 1) and not download_search:
                if have_obs:
                    entries_table = ObservationsTable(queryset,
                                                      template='table.html')
                    prev_time = calc_duration('create table2', prev_time)
                    RequestConfig(request).configure(entries_table)
                    prev_time = calc_duration('RequestConfig configure', prev_time)

                    context['entries'] = entries_table
                else:
                    context['entries'] = None
                if num_photos < MAX_PHOTO_IN_GALLERY:
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
