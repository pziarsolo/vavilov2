from django_tables2.config import RequestConfig

from vavilov.models import Trait
from vavilov.views.tables import ObservationsTable
from django.views.generic.detail import DetailView
from guardian.mixins import PermissionRequiredMixin


class TraitDetail(PermissionRequiredMixin, DetailView):
    model = Trait
    slug_url_kwarg = 'trait_id'
    slug_field = 'trait_id'
    permission_required = 'view_trait'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TraitDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['trait'] = self.object

        # Observations
        observations_table = ObservationsTable(self.object.observations(user),
                                               template='table.html',
                                               prefix='observations-')
        RequestConfig(self.request).configure(observations_table)
        context['observations'] = observations_table
        context['obs_search_criteria'] = {'traits': self.object.name}

        return context
