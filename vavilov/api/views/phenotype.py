from rest_framework.filters import (DjangoObjectPermissionsFilter,
                                    DjangoFilterBackend)
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from vavilov.api.filters import AssayFilter, PlantFilter
from vavilov.api.permissions import CustomObjectPermissions, IsStaffOrReadOnly
from vavilov.api.serializers import (AssaySerializer, PlantSerializer,
                                     AssayPlantSerializer, AssayPropSerializer,
                                     PlantPartSerializer)
from vavilov.models import (Assay, Plant, AssayPlant, AssayProp, PlantPart)


class AssayViewSet(ModelViewSet):
    lookup_field = 'name'
    queryset = Assay.objects.all()
    serializer_class = AssaySerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,
                       DjangoFilterBackend)

    filter_class = AssayFilter


class AssayPropViewSet(ModelViewSet):
    queryset = AssayProp.objects.all()
    serializer_class = AssayPropSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,
                       DjangoFilterBackend)


class PlantViewSet(ModelViewSet):
    lookup_field = 'plant_name'
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,
                       DjangoFilterBackend)

    filter_class = PlantFilter


class PlantPartViewSet(ModelViewSet):
    queryset = PlantPart.objects.all()
    serializer_class = PlantPartSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter,
                       DjangoFilterBackend)

    filter_class = PlantFilter


class AssayPlantViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = AssayPlant.objects.all()
    serializer_class = AssayPlantSerializer
    permission_classes = (IsStaffOrReadOnly,)
#     filter_backends = (DjangoObjectPermissionsFilter,
#                        DjangoFilterBackend)
#     filter_class = PlantFilter
