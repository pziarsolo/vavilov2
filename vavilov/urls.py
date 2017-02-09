from django.conf import settings as site_settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.core.exceptions import ImproperlyConfigured

from vavilov.conf import settings
from vavilov.views.observation import ObservationImageList, ObservationList, \
    ObservationEntityDetail
from vavilov.views.accession import AccessionList, AccessionDetail
from vavilov.views.plant import PlantDetail
from vavilov.views.assay import AssayDetail
from vavilov.views.trait import TraitDetail


urlpatterns = [
    url(r'^plant/(?P<plant_name>.+)/$', PlantDetail.as_view(), name='plant-detail'),
    url(r'^assay/(?P<name>.+)/$', AssayDetail.as_view(), name='assay-detail'),
    url(r'^trait/(?P<trait_id>.+)/$', TraitDetail.as_view(), name='trait-detail'),
    # url(r'^accession/(?P<accession_number>.+)/$', 'vavilov.views.accession.accession', name='accession-detail'),
    url(r'^obs_entity/(?P<name>.+)/$', ObservationEntityDetail.as_view(), name='obs_entity-detail'),

    url(r'^observation_images/$', ObservationImageList.as_view(), name='observation-listimage'),
    url(r'^observations/$', ObservationList.as_view(), name='observation-list'),

    url(r'^accessions/(?P<accession_number>.+)/$', AccessionDetail.as_view(),
        name='accession-detail'),
    url(r'^accessions/$', AccessionList.as_view(), name='accession-list'),

    url(r'^apis/accession_numbers/$', 'vavilov.views.api.accession_numbers', name='api_accession_numbers'),
    url(r'^apis/taxons/$', 'vavilov.views.api.taxons', name='api_taxons'),
    url(r'^apis/plants/$', 'vavilov.views.api.plants', name='api_plants'),
    url(r'^apis/traits/$', 'vavilov.views.api.traits', name='api_traits'),
]

if settings.EXPOSE_API:
    urlpatterns += [url(r'', include('vavilov.api.urls')), ]

if site_settings.DEVELOPMENT_MACHINE:
    try:
        urlpatterns += static(site_settings.MEDIA_URL,
                              document_root=site_settings.MEDIA_ROOT)
    except ImproperlyConfigured:
        pass
