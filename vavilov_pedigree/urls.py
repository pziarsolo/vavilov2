from django.conf.urls import url, include
from vavilov_pedigree.views.entities import (AccessionDetail, AssayDetail,
                                             PlantDetail, SeedLotDetail)

pedigree_urlpatterns = [
    url(r'^assay/(?P<name>.+)/$', AssayDetail, name='assay-detail'),
    url(r'^seedlot/(?P<name>.+)/$', SeedLotDetail.as_view(), name='seedlot-detail'),
    url(r'^accession/(?P<accession_number>.+)/$', AccessionDetail.as_view(), name='accession-detail'),
    url(r'^plant/(?P<plant_name>.+)/$', PlantDetail.as_view(), name='plant-detail'),
    url(r'^search/cross_experiment/$', 'vavilov_pedigree.views.entities.search_cross', name='search_pedigree_cross'),
    url(r'^search/seed_lot/$', 'vavilov_pedigree.views.entities.search_seedlot', name='search_pedigree_seedlot'),
]

urlpatterns = [
    url(r'', include(pedigree_urlpatterns, namespace='pedigree')),
]
