from rest_framework.filters import DjangoObjectPermissionsFilter
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
from django_filters.rest_framework.backends import DjangoFilterBackend


class AssayViewSet(ModelViewSet):
    lookup_field = 'name'
    queryset = Assay.objects.all()
    serializer_class = AssaySerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter, DjangoFilterBackend)

    filter_class = AssayFilter


class AssayPropViewSet(ModelViewSet):
    queryset = AssayProp.objects.all()
    serializer_class = AssayPropSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter, DjangoFilterBackend)


class PlantViewSet(ModelViewSet):
    lookup_field = 'plant_name'
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter, DjangoFilterBackend)

    filter_class = PlantFilter


class ObservationEntityViewSet(ModelViewSet):
    queryset = ObservationEntity.objects.all()
    serializer_class = ObservationEntitySerializer
    permission_classes = (CustomObjectPermissions,)
    filter_backends = (DjangoObjectPermissionsFilter, DjangoFilterBackend)

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
                                  'exp_id': ''}
                data.append(fielbook_entry)
        except Exception:
            return Response({'detail: Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data)

    def create(self, request):
        plant_part = 'plant'
        assay = request.data.get('assay', None)

        if request.data:
            try:
                _, created = add_fieldbook_observations(request.data,
                                                        plant_part=plant_part,
                                                        assay=assay)
                if created:
                    return Response(data=request.data,
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response(data={'detail': 'Already in db'},
                                    status=status.HTTP_200_OK)
            except MultiValueDictKeyError as error:
                return Response(exception=error, status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': 'Incorrect input data'})
            except ValueError as error:
                if 'Trait not loaded yet in db' in str(error):
                    return Response(exception=error, status=status.HTTP_400_BAD_REQUEST,
                                    data={'detail': str(error)})
            except Plant.DoesNotExist as error:
                return Response(exception=error, status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': str(error)})
            except Assay.DoesNotExist as error:
                return Response(exception=error, status=status.HTTP_400_BAD_REQUEST,
                                data={'detail': str(error)})

#         if len(request.data) != 1:
        data = {'msg': 'no data provided'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
