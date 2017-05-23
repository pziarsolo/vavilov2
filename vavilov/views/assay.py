
from django.views.generic.detail import DetailView

from vavilov.models import Assay
from vavilov.views.tables import plants_to_table, obs_to_table
# from vavilov.views.observation import observations_to_galleria_json
from vavilov.permissions import PermissionRequiredMixin


class AssayDetail(PermissionRequiredMixin, DetailView):
    model = Assay
    slug_url_kwarg = 'name'
    slug_field = 'name'
    permission_required = ['vavilov.view_assay']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AssayDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['assay'] = self.object

        # plants
        plants = self.object.plants(user)
        context['plants'] = plants_to_table(plants, self.request) if plants else None

        # Observations
        obs = self.object.observations(user)
        context['observations'] = obs_to_table(obs, self.request) if obs else None

        # context['json_images'] = observations_to_galleria_json(self.object.obs_images(user))
        # search criteria
        context['obs_search_criteria'] = {'assay': self.object.name}
        return context
