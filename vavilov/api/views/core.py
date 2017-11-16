from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from vavilov.api.filters import CvtermFilter, CvFilter, DbFilter, CountryFilter
from vavilov.api.permissions import UserPermission, IsStaffOrReadOnly
from vavilov.api.serializers import (PersonSerializer,
                                     PersonRelationshipSerializer,
                                     TaxaRelationshipSerializer, TaxaSerializer,
                                     CvtermSerializer, GroupSerializer,
                                     UserSerializer, PasswordSerializer,
                                     CountrySerializer, CvSerializer, DbSerializer)
from vavilov.models import (Person, PersonRelationship,
                            TaxaRelationship, Taxa, Cvterm, Country, Cv, Db)
from django_filters.rest_framework.backends import DjangoFilterBackend


class UserViewSet(ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)

    @detail_route(methods=['post'])
    def set_password(self, request, username=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(ModelViewSet):
    lookup_field = 'name'
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAdminUser,)


class DbViewSet(ModelViewSet):
    queryset = Db.objects.all()
    serializer_class = DbSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = DbFilter


class CvtermViewSet(ModelViewSet):
    queryset = Cvterm.objects.all()
    serializer_class = CvtermSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = CvtermFilter


class CvViewSet(ModelViewSet):
    lookup_field = 'name'
    queryset = Cv.objects.all()
    serializer_class = CvSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = CvFilter


class CountryViewSet(ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = CountryFilter


class PersonViewSet(ModelViewSet):
    lookup_field = 'name'
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsStaffOrReadOnly,)


class PersonRelationsViewSet(ModelViewSet):
    queryset = PersonRelationship.objects.all()
    serializer_class = PersonRelationshipSerializer
    permission_classes = (IsStaffOrReadOnly,)


class TaxaViewSet(ModelViewSet):
    queryset = Taxa.objects.all()
    serializer_class = TaxaSerializer
    permission_classes = (IsStaffOrReadOnly,)


class TaxaRelationsViewSet(ModelViewSet):
    queryset = TaxaRelationship.objects.all()
    serializer_class = TaxaRelationshipSerializer
    permission_classes = (IsStaffOrReadOnly,)
