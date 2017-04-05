from django.conf.urls import url, include

from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from vavilov.api.views import core, accession, phenotype


API_TITLE = 'Vavilov API DOC'
API_DESCRIPTION = '...'

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

schema_view = get_schema_view(title="Server Monitoring API")

urlpatterns = [
    url('^api/schemma$', schema_view),
    url(r'^api/docs/', include_docs_urls(title=API_TITLE,
                                         description=API_DESCRIPTION)),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework'))

]
