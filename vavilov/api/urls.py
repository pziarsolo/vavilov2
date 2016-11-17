from django.conf.urls import url, include

from rest_framework import routers

from vavilov.api.views import core, accession, phenotype


# rest_api
router = routers.DefaultRouter()
router.register(r'users', core.UserViewSet)
router.register(r'groups', core.GroupViewSet)
router.register(r'dbs', core.DbViewSet)
router.register(r'cvs', core.CvViewSet)
router.register(r'cvterms', core.CvtermViewSet)
router.register(r'countrys', core.CountryViewSet)
router.register(r'accessions', accession.AccessionViewSet)
router.register(r'accessionrelations', accession.AccessionRelationsViewSet)
router.register(r'accessiontaxas', accession.AccessionTaxaViewSet)
router.register(r'accession_synonyms', accession.AccessionSynonymViewSet)
router.register(r'passports', accession.PassportViewSet)
router.register(r'locations', accession.LocationViewSet)
router.register(r'persons', core.PersonViewSet)
router.register(r'person_relationships', core.PersonRelationsViewSet)
router.register(r'taxas', core.TaxaViewSet)
router.register(r'taxa_relationships', core.TaxaRelationsViewSet)
router.register(r'assays', phenotype.AssayViewSet)
router.register(r'assayprop', phenotype.AssayPropViewSet)
router.register(r'plants', phenotype.PlantViewSet)
router.register(r'assayplants', phenotype.AssayPlantViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework'))
]
