from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_tables2 import RequestConfig
from django_tables2.utils import A
from guardian.decorators import permission_required

import django_tables2 as tables

from vavilov.models import Plant
from vavilov.views.observation import ObservationsTable


class PlantsTable(tables.Table):
    plant = tables.LinkColumn('plant_view', args=[A('unique_id')],
                              accessor=A('unique_id'), orderable=True,
                              verbose_name='Plant')
    Accession = tables.LinkColumn('accession_view', args=[A('accession.code')],
                                  accessor=A('accession.code'),
                                  orderable=True, verbose_name='Accession')
    Exp_field = tables.Column('Experimentalfield',
                              accessor=A('experimental_field'))
    row = tables.Column('Row', accessor=A('row'))
    column = tables.Column('Column', accessor=A('column'))
    pot_number = tables.Column('Pot number', accessor=A('pot_number'))

    class Meta:
        attrs = {"class": "searchresult"}


class AssaysTable(tables.Table):
    assay = tables.LinkColumn('assay_view', args=[A('name')],
                              accessor=A('name'),
                              orderable=True, verbose_name='Assay')
    description = tables.Column('Description', accessor=A('description'))
    owner = tables.Column('Owner', accessor=A('owner.username'),
                          orderable=True)
    start_date = tables.Column('Start date', accessor=A('start_date'))
    end_date = tables.Column('End date', accessor=A('end_date'))
    location = tables.Column('Location', accessor=A('location'))
    campaign = tables.Column('Campaign', accessor=A('campaign'))

    class Meta:
        attrs = {"class": "searchresult"}


@permission_required('view_plant', (Plant, 'unique_id', 'unique_id'))
def plant(request, unique_id):
    user = request.user
    context = RequestContext(request)
    try:
        plant = Plant.objects.get(unique_id=unique_id)
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
    context['obs_search_criteria'] = {'plant': unique_id}

    template = 'plant.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)
