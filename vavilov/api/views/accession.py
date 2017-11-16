from rest_framework.filters import (DjangoObjectPermissionsFilter)
from rest_framework.viewsets import ModelViewSet

from vavilov.api.filters import AccessionFilter
from vavilov.api.permissions import CustomObjectPermissions
from vavilov.api.serializers import (AccessionSerializer,
                                     AccessionRelationSerializer,
                                     AccessionSynonymSerializer,
                                     PassportSerializer, LocationSerializer,
                                     AccessionTaxaSerializer)
from vavilov.models import (Accession, AccessionRelationship, AccessionSynonym,
                            Passport, Location, AccessionTaxa)
from django_filters.rest_framework.backends import DjangoFilterBackend


class AccessionViewSet(ModelViewSet):
    lookup_field = 'accession_number'
    queryset = Accession.objects.all()
    serializer_class = AccessionSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter, DjangoFilterBackend)

    filter_class = AccessionFilter


class AccessionRelationsViewSet(ModelViewSet):
    queryset = AccessionRelationship.objects.all()
    serializer_class = AccessionRelationSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,)


class AccessionTaxaViewSet(ModelViewSet):
    queryset = AccessionTaxa.objects.all()
    serializer_class = AccessionTaxaSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,)


class AccessionSynonymViewSet(ModelViewSet):
    queryset = AccessionSynonym.objects.all()
    serializer_class = AccessionSynonymSerializer


class PassportViewSet(ModelViewSet):
    queryset = Passport.objects.all()
    serializer_class = PassportSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,)


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,)
