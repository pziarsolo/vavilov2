from django_tables2 import RequestConfig

from vavilov.models import Plant
from vavilov.views.tables import AssaysTable, ObservationsTable
from guardian.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView


class PlantDetail(PermissionRequiredMixin, DetailView):
    model = Plant
    slug_url_kwarg = 'plant_name'
    slug_field = 'plant_name'
    permission_required = 'view_plant'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PlantDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['plant'] = self.object
        # Assays
        assay_table = AssaysTable(self.object.assays(user), template='table.html',
                                  prefix='assays-')
        RequestConfig(self.request).configure(assay_table)
        context['assays'] = assay_table

        # Observations
        observations_table = ObservationsTable(self.object.observations(user),
                                               template='table.html',
                                               prefix='observations-')
        RequestConfig(self.request).configure(observations_table)
        context['observations'] = observations_table

        context['obs_images'] = self.object.obs_images(user)
        # search_criteria
        context['obs_search_criteria'] = {'plant': self.object.plant_name}

        return context
