from django.views.generic.detail import DetailView
from django.template.context import RequestContext
from django.template.context_processors import csrf

from django_tables2 import RequestConfig
from guardian.mixins import PermissionRequiredMixin

from vavilov.forms.observations import SearchObservationForm
from vavilov.models import ObservationEntity, filter_observations, Observation
from vavilov.views.tables import ObservationsTable, PlantsTable
from vavilov.conf.settings import MAX_PHOTO_IN_GALLERY
from vavilov.views.generic import SearchListView


class ObservationList(SearchListView):
    model = Observation
    template_name = 'vavilov/observation-list.html'
    form_class = SearchObservationForm
    table = ObservationsTable
    detail_view_name = None

    def get_queryset(self, **kwargs):
        return filter_observations(kwargs['search_criteria'],
                                   user=kwargs['user'])


class ObservationImageList(SearchListView):
    model = Observation
    template_name = 'vavilov/observation-listimages.html'
    form_class = SearchObservationForm
    table = ''
    detail_view_name = None

    def get_queryset(self, **kwargs):
        obs = filter_observations(kwargs['search_criteria'],
                                   user=kwargs['user'], images=True)
        return obs

    def get_context_data(self, **kwargs):
        context = RequestContext(self.request)
        context.update(kwargs)
        context.update(csrf(self.request))
        num_photos = self.object_list.count()
        if num_photos > MAX_PHOTO_IN_GALLERY:
            self.object_list = None
        context.update({'object_list': self.object_list})
        return context


class ObservationEntityDetail(PermissionRequiredMixin, DetailView):
    model = ObservationEntity
    slug_url_kwarg = 'name'
    slug_field = 'name'
    permission_required = 'view_obs_entity'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ObservationEntityDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['obs_entity'] = self.object

        if self.object:
            plants = self.object.plants(user)
            if plants:
                plant_table = PlantsTable(plants, template='table.html',
                                          prefix='plant-')
                RequestConfig(self.request).configure(plant_table)
            else:
                plant_table = None
            context['plants'] = plant_table

            obs = self.object.observations(user)
            if obs:
                observations_table = ObservationsTable(obs, template='table.html',
                                                       prefix='observations-')
                RequestConfig(self.request).configure(observations_table)
            else:
                observations_table = None

            context['observations'] = observations_table
            context['obs_images'] = self.object.obs_images(user)
        return context
