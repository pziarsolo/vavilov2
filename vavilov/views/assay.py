from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_tables2.config import RequestConfig
from guardian.decorators import permission_required

from vavilov.models import Assay
from vavilov.views.tables import PlantsTable, ObservationsTable


@permission_required('view_assay', (Assay, 'name', 'name'))
def assay(request, name):
    user = request.user
    context = RequestContext(request)
    try:
        assay = Assay.objects.get(name=name)
    except Assay.DoesNotExist:
        assay = None
    context['assay'] = assay

    # plants
    plants = assay.plants(user)
    if plants:
        plant_table = PlantsTable(plants, template='table.html',
                                  prefix='plant-')
        RequestConfig(request).configure(plant_table)
    else:
        plant_table = None
    context['plants'] = plant_table

    # Observations
    obs = assay.observations(user)
    if obs:
        observations_table = ObservationsTable(obs, template='table.html',
                                               prefix='observations-')
        RequestConfig(request).configure(observations_table)
    else:
        observations_table = None
    context['observations'] = observations_table

    context['obs_images'] = assay.obs_images(user)
    # search criteria
    context['obs_search_criteria'] = {'assay': name}

    template = 'vavilov/assay.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)
