from django.conf.urls import url

urlpatterns = [
    url(r'^plant/(?P<plant_name>.+)/$', 'vavilov_pedigree.views.entities.plant', name='pedigree_plant_view'),
    url(r'^assay/(?P<name>.+)/$', 'vavilov_pedigree.views.entities.assay', name='pedigree_assay_view'),
    url(r'^seedlot/(?P<name>.+)/$', 'vavilov_pedigree.views.entities.seed_lot', name='pedigree_seedlot_view'),
    url(r'^accession/(?P<accession_number>.+)/$', 'vavilov_pedigree.views.entities.accession', name='pedigree_accession_view'),
    url(r'^search/cross_experiment/$', 'vavilov_pedigree.views.entities.search_cross', name='search_pedigree_cross'),
    url(r'^search/seed_lot/$', 'vavilov_pedigree.views.entities.search_seedlot', name='search_pedigree_seedlot'),
]
