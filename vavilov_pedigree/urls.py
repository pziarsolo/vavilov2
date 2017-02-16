from django.conf.urls import url, include
from vavilov_pedigree.views.details import (AccessionDetail, AssayDetail,
                                            PlantDetail, SeedLotDetail)
from vavilov_pedigree.views.search import search, CrossExperiments

pedigree_urlpatterns = [
    url(r'^assays/(?P<name>.+)/$', AssayDetail, name='assay-detail'),
    url(r'^seedlots/(?P<name>.+)/$', SeedLotDetail.as_view(), name='seedlot-detail'),
    url(r'^accessions/(?P<accession_number>.+)/$', AccessionDetail.as_view(), name='accession-detail'),
    url(r'^plants/(?P<plant_name>.+)/$', PlantDetail.as_view(), name='plant-detail'),
    url(r'^search/$', search, name='search'),
    url(r'^cross_experiments/$', CrossExperiments.as_view(), name='cross_exp-list')
]

urlpatterns = [
    url(r'', include(pedigree_urlpatterns, namespace='pedigree')),
]
