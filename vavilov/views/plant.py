from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_tables2 import RequestConfig
from guardian.decorators import permission_required

from vavilov.models import Plant
from vavilov.views.tables import AssaysTable, ObservationsTable


@permission_required('view_plant', (Plant, 'plant_name', 'plant_name'))
def plant(request, plant_name):
    user = request.user
    context = RequestContext(request)
    try:
        plant = Plant.objects.get(plant_name=plant_name)
    except Plant.DoesNotExist:
        plant = None
    context['plant'] = plant
    # Assays
    assay_table = AssaysTable(plant.assays(user), template='table.html',
                              prefix='assays-')
    RequestConfig(request).configure(assay_table)
    context['assays'] = assay_table

    # Observations
    observations_table = ObservationsTable(plant.observations(user),
                                           template='table.html',
                                           prefix='observations-')
    RequestConfig(request).configure(observations_table)
    context['observations'] = observations_table

    context['obs_images'] = plant.obs_images(user)
    # search_criteria
    context['obs_search_criteria'] = {'plant': plant_name}

    template = 'vavilov/plant.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)
