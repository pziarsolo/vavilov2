from django.views.generic.detail import DetailView
from guardian.mixins import PermissionRequiredMixin

from vavilov.models import Plant
from vavilov.views.tables import assays_to_table, obs_to_table


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
        # assays
        assays = self.object.assays(user)
        context['assays'] = assays_to_table(assays, self.request) if assays else None

        # Observations
        obs = self.object.observations(user)
        context['observations'] = obs_to_table(obs, self.request) if obs else None

        context['obs_images'] = self.object.obs_images(user)
        # search_criteria
        context['obs_search_criteria'] = {'plant': self.object.plant_name}

        return context
