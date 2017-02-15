from django.conf.urls import url, include
from vavilov_pedigree.views.details import (AccessionDetail, AssayDetail,
                                            PlantDetail, SeedLotDetail)
from vavilov_pedigree.views.search import SearchView

pedigree_urlpatterns = [
    url(r'^assay/(?P<name>.+)/$', AssayDetail, name='assay-detail'),
    url(r'^seedlot/(?P<name>.+)/$', SeedLotDetail.as_view(), name='seedlot-detail'),
    url(r'^accession/(?P<accession_number>.+)/$', AccessionDetail.as_view(), name='accession-detail'),
    url(r'^plant/(?P<plant_name>.+)/$', PlantDetail.as_view(), name='plant-detail'),
    url(r'^search/$', SearchView.as_view(), name='search'),
]

urlpatterns = [
    url(r'', include(pedigree_urlpatterns, namespace='pedigree')),
]
