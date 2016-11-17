from django.conf import settings as site_settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from vavilov.conf import settings

urlpatterns = [
    url(r'^plant/(?P<unique_id>.+)/$', 'vavilov.views.plant.plant', name='plant_view'),
    url(r'^assay/(?P<name>.+)/$', 'vavilov.views.assay.assay', name='assay_view'),
    url(r'^trait/(?P<trait_id>.+)/$', 'vavilov.views.trait.trait', name='trait_view'),
    url(r'^accession/(?P<accession_number>.+)/$', 'vavilov.views.accession.accession', name='accession'),
    url(r'^search/accession/$', 'vavilov.views.accession.search', name='search_accession'),
    url(r'^search/observations/$', 'vavilov.views.observation.search', name='search_observations'),
    url(r'^apis/accession_numbers/$', 'vavilov.views.api.accession_numbers', name='api_accession_numbers'),
    url(r'^apis/taxons/$', 'vavilov.views.api.taxons', name='api_taxons'),
    url(r'^apis/plants/$', 'vavilov.views.api.plants', name='api_plants'),
]

if settings.EXPOSE_API:
    urlpatterns += [url(r'', include('vavilov.api.urls')), ]

if site_settings.DEVELOPMENT_MACHINE:
    urlpatterns += static(site_settings.MEDIA_URL,
                          document_root=site_settings.MEDIA_ROOT)
