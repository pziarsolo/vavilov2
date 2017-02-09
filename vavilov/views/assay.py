from guardian.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView
from django_tables2.config import RequestConfig

from vavilov.models import Assay
from vavilov.views.tables import PlantsTable, ObservationsTable


class AssayDetail(PermissionRequiredMixin, DetailView):
    model = Assay
    slug_url_kwarg = 'name'
    slug_field = 'name'
    permission_required = 'view_assay'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AssayDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['assay'] = self.object

        # plants
        plants = self.object.plants(user)
        if plants:
            plant_table = PlantsTable(plants, template='table.html',
                                      prefix='plant-')
            RequestConfig(self.request).configure(plant_table)
        else:
            plant_table = None
        context['plants'] = plant_table

        # Observations
        obs = self.object.observations(user)
        if obs:
            observations_table = ObservationsTable(obs, template='table.html',
                                                   prefix='observations-')
            RequestConfig(self.request).configure(observations_table)
        else:
            observations_table = None
        context['observations'] = observations_table

        context['obs_images'] = self.object.obs_images(user)
        # search criteria
        context['obs_search_criteria'] = {'assay': self.object.name}
        return context
