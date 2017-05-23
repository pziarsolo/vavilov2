from time import time
import json

from django.views.generic.detail import DetailView
from django.template.context_processors import csrf

from vavilov.forms.observations import SearchObservationForm
from vavilov.models import ObservationEntity, filter_observations, Observation
from vavilov.views.tables import (ObservationsTable, plants_to_table,
                                  obs_to_table)
from vavilov.conf.settings import MAX_PHOTO_IN_GALLERY
from vavilov.views.generic import SearchListView, calc_duration
from vavilov.permissions import PermissionRequiredMixin


class ObservationList(SearchListView):
    model = Observation
    template_name = 'vavilov/observation-list.html'
    form_class = SearchObservationForm
    table = ObservationsTable
    detail_view_name = None

    def get_queryset(self, **kwargs):
        return filter_observations(kwargs['search_criteria'],
                                   user=kwargs['user'])


def observations_to_galleria_json(obs):
    prev_time = time()
    obs_data = [{'image': o.image.url, 'thumb': o.thumbnail.url, 'title': 'Assay=' + o.assay.name} for o in obs]
    prev_time = calc_duration('Observation_to_dict_images', prev_time)
    json_data = json.dumps(obs_data)
    prev_time = calc_duration('Dict_images_to_json_images', prev_time)
    return json_data


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
        context = {'request': self.request}
        context['user'] = self.request.user
        context.update(kwargs)
        context.update(csrf(self.request))
        context['query_made'] = kwargs['query_made']
        prev_time = time()
        num_photos = self.object_list.count()
        prev_time = calc_duration('Count images', prev_time)

        if num_photos > MAX_PHOTO_IN_GALLERY:
            self.object_list = None
            warning_ = 'Too much photos({}) to show. More than max allowed({}).'
            warning_ += 'Try to filter them'
            warning_ = warning_.format(num_photos, MAX_PHOTO_IN_GALLERY)
            json_images = json.dumps([])
        else:
            warning_ = None
            json_images = observations_to_galleria_json(obs=self.object_list)

        context['warning'] = warning_
        context['json_images'] = json_images
        context.update({'object_list': self.object_list})
        return context


class ObservationEntityDetail(PermissionRequiredMixin, DetailView):
    model = ObservationEntity
    slug_url_kwarg = 'name'
    slug_field = 'name'
    permission_required = ['vavilov.view_obs_entity']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ObservationEntityDetail, self).get_context_data(**kwargs)
        user = self.request.user

        context['obs_entity'] = self.object

        if self.object:
            plants = self.object.plants(user)
            context['plants'] = plants_to_table(plants, self.request) if plants else None

            obs = self.object.observations(user)
            context['observations'] = obs_to_table(obs, self.request) if obs else None
            context['json_images'] = observations_to_galleria_json(self.object.obs_images(user))
        return context
