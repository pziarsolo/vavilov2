from rest_framework.filters import (DjangoObjectPermissionsFilter,
                                    DjangoFilterBackend)
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ViewSet

from vavilov.api.filters import AssayFilter, PlantFilter
from vavilov.api.permissions import CustomObjectPermissions, IsStaffOrReadOnly
from vavilov.api.serializers import (AssaySerializer, PlantSerializer,
                                     AssayPlantSerializer, AssayPropSerializer,
                                     ObservationEntitySerializer)
from vavilov.models import (Assay, Plant, AssayPlant, AssayProp,
                            ObservationEntity, Observation, TraitProp)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from vavilov.db_management.fieldbook import (to_fieldbook_local_time,
                                             FIELBOOK_TRAIT_TYPE,
                                             add_fieldbook_observations)
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.models import Group
from rest_framework import status


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


class ObservationEntityViewSet(ModelViewSet):
    queryset = ObservationEntity.objects.all()
    serializer_class = ObservationEntitySerializer
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


class FieldBookObservationViewSet(ViewSet):
    queryset = Observation.objects.all()[:200]
    permission_classes = (IsAuthenticated,)
    base_name = 'fieldbook_observations'

    def list(self, request):

        queryset = self.queryset
        data = []
        try:
            for observation in queryset:
                local_creation_time = to_fieldbook_local_time(observation.creation_time)
                try:
                    # If trait is not fieldbook type it should not be returned
                    fieldbook_trait_type = TraitProp.objects.get(trait=observation.trait,
                                                                 type__name=FIELBOOK_TRAIT_TYPE)
                except TraitProp.DoesNotExist:
                    continue
                plant_name = observation.plants[0].plant_name
                fielbook_entry = {'rid': plant_name, 'parent': observation.trait.name,
                                  'trait': fieldbook_trait_type.value,
                                  'userValue': observation.value,
                                  'timeTaken': local_creation_time,
                                  'person': observation.observer,
                                  'location': '', 'rep': '1', 'notes': '',
                                  'exp_i': ''}
                data.append(fielbook_entry)
        except Exception:
            return Response({'msg: Internal server error'}, status=500)

        return Response(data)

    def create(self, request):
        plant_part = 'plant'
        assay = 'assay1'
        group = Group.objects.get(name=assay)
        if request.data:
            try:
                _, created = add_fieldbook_observations(request.data,
                                                        plant_part=plant_part,
                                                        assay=assay,
                                                        group=group)
                if created:
                    return Response(data=request.data, status=201)
                else:
                    return Response(data={'detail': 'Already in db'},
                                    status=status.HTTP_200_OK)
            except MultiValueDictKeyError as error:
                return Response(exception=error, status=400,
                                data={'detail': 'Incorrect input data'})

#         if len(request.data) != 1:
        data = {'msg': 'some error'}
        return Response(data=data, status=400)

