from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_tables2.config import RequestConfig
from guardian.decorators import permission_required

from vavilov.models import Trait
from vavilov.views.observation import ObservationsTable


@permission_required('view_trait', (Trait, 'trait_id', 'trait_id'))
def trait(request, trait_id):
    user = request.user
    context = RequestContext(request)
    try:
        trait = Trait.objects.get(trait_id=trait_id)
    except trait.DoesNotExist:
        trait = None
    context['trait'] = trait

    # Observations
    observations_table = ObservationsTable(trait.observations(user),
                                           template='table.html',
                                           prefix='observations-')
    RequestConfig(request).configure(observations_table)
    context['observations'] = observations_table

    template = 'trait.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)
