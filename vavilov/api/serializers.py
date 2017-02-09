from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers
from rest_framework.permissions import IsAdminUser

from vavilov.models import (Accession, Cvterm, AccessionRelationship,
                            AccessionSynonym, Passport, Location, Person,
                            PersonRelationship, Taxa, TaxaRelationship,
                            Country, Cv, Db, Pub, AccessionProp, AccessionTaxa,
                            Assay, Plant, AssayPlant, AssayProp,
                            ObservationEntity)


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField()


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'password', 'email', 'first_name',
                  'last_name')

    def create(self, validated_data):
        user = UserModel.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),

        )
        user.set_password(validated_data['password'])
        user.save()
        # add to public group
        public_group = Group.objects.get_or_create(name='public')[0]
        public_group.user_set.add(user)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        permission_classes = (IsAdminUser,)
        model = Group
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class DbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Db
        fields = '__all__'


class DbxrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cvterm
        fields = ('db', 'accession_name')


class CvtermSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:cvterm-detail',
                                               lookup_field='pk')

    class Meta:
        model = Cvterm
        fields = ['url', 'cvterm_id', 'name', 'definition', 'cv']
        extra_kwargs = {'cv': {'lookup_field': 'name'}}


class CvSerializer(serializers.ModelSerializer):
    cvterms = CvtermSerializer(read_only=True, many=True)

    class Meta:
        model = Cv
        fields = '__all__'


class TaxaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxa
        fields = '__all__'


class TaxaRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxaRelationship
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['person_id', 'name', 'description', 'type']


class PersonRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonRelationship
        fields = '__all__'


class PubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pub
        fields = '__all__'


class AccessionSerializer(serializers.ModelSerializer):
    duplicated_accessions = serializers.HyperlinkedRelatedField(read_only=True,
                                                                many=True,
                                                                lookup_field='accession_number',
                                                                view_name='api:accession-detail')
    passport = serializers.HyperlinkedRelatedField(read_only=True,
                                                   view_name='api:passport-detail')
    collecting_province = serializers.StringRelatedField(read_only=True)
    collecting_country = serializers.StringRelatedField(read_only=True)
    collecting_region = serializers.StringRelatedField(read_only=True)
    local_name = serializers.StringRelatedField(read_only=True)
    collecting_date = serializers.StringRelatedField(read_only=True)
    organism = serializers.StringRelatedField(read_only=True)
#     donor_accession = serializers.HyperlinkedRelatedField(read_only=True,
#                                                           allow_null=True,
#                                                           view_name='accession-detail')

    class Meta:
        model = Accession
        fields = ('accession_id', 'accession_number', 'institute', 'type',
                  'duplicated_accessions', 'passport', 'collecting_province',
                  'collecting_country', 'collecting_region', 'local_name',
                  'collecting_date', 'organism')  # , 'donor_accession')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class PassportSerializer(serializers.ModelSerializer):
    location = serializers.HyperlinkedRelatedField(read_only=True,
                                                   view_name='api:location-detail')

    class Meta:
        model = Passport
        fields = '__all__'


class AccessionPropSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessionProp
        fields = '__all__'


class AccessionTaxaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessionTaxa
        fields = '__all__'


class AccessionRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessionRelationship
        fields = '__all__'


class AccessionSynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessionSynonym
        fields = '__all__'
        # fields = ('accession', 'synonym_institute', 'synonym_code', 'type')


class PlantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant
        fields = '__all__'


class AssayPropSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssayProp
        fields = '__all__'


class AssaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Assay
        fields = ['url', 'assay_id', 'name', 'owner', 'description']
        extra_kwargs = {
            'url': {'view_name': 'assay-detail', 'lookup_field': 'name'},
            'owner': {'view_name': 'user-detail', 'lookup_field': 'username'}}


class AssayPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssayPlant
        fields = '__all__'


class ObservationEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationEntity
        fields = '__all__'
