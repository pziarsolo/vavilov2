from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_tables2.config import RequestConfig
from guardian.decorators import permission_required

from vavilov.models import Assay
from vavilov.views.observation import ObservationsTable
from vavilov.views.plant import PlantsTable


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
    plant_table = PlantsTable(assay.plants(user), template='table.html',
                              prefix='plant-')
    RequestConfig(request).configure(plant_table)
    context['plants'] = plant_table

    # Observations
    observations_table = ObservationsTable(assay.observations(user),
                                           template='table.html',
                                           prefix='observation-')
    RequestConfig(request).configure(observations_table)
    context['observations'] = observations_table

    context['obs_images'] = assay.obs_images(user)
    # search criteria
    context['obs_search_criteria'] = {'assay': name}

    template = 'assay.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)
