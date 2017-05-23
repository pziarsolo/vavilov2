from django.views.generic.detail import DetailView

from vavilov.models import Trait
from vavilov.views.tables import obs_to_table
from vavilov.permissions import PermissionRequiredMixin


class TraitDetail(PermissionRequiredMixin, DetailView):
    model = Trait
    slug_url_kwarg = 'trait_id'
    slug_field = 'trait_id'
    permission_required = ['vavilov.view_trait']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TraitDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['trait'] = self.object

        # Observations
        obs = self.object.observations(user)
        context['observations'] = obs_to_table(obs, self.request) if obs else None
        context['obs_search_criteria'] = {'traits': self.object.name}

        return context
