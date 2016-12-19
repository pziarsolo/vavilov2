from collections import OrderedDict
from functools import reduce
import operator

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from guardian.shortcuts import get_objects_for_user

from vavilov.conf.settings import GENEBANK_CODE, PHENO_PHOTO_DIR
from vavilov.utils.storage import OnlyScanStorage


class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    code2 = models.CharField(max_length=2, db_index=True)
    code3 = models.CharField(max_length=3, db_index=True)
    name = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'vavilov_country'

    def __str__(self):
        return '{}({})'.format(self.name, self.code2)


class Db(models.Model):
    db_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=48, unique=True)
    description = models.CharField(max_length=255, null=True)
    urlprefix = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'vavilov_db'


class Dbxref(models.Model):
    dbxref_id = models.AutoField(primary_key=True)
    db = models.ForeignKey(Db)
    accession_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'vavilov_dbxref'
        unique_together = ('db', 'accession_name')


class Cv(models.Model):
    cv_id = models.AutoField(primary_key=True)
    name = models.CharField(db_index=True, max_length=48, unique=True)
    description = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'vavilov_cv'

    def __str__(self):
        return self.name


class Cvterm(models.Model):
    cvterm_id = models.AutoField(primary_key=True)
    cv = models.ForeignKey(Cv)
    name = models.CharField(db_index=True, max_length=255)
    definition = models.CharField(max_length=255, null=True)
    dbxref = models.ForeignKey(Dbxref, null=True)

    class Meta:
        db_table = 'vavilov_cvterm'
        unique_together = ('cv', 'name')

    def __str__(self):
        return '{}: {}'.format(self.cv.name, self.name)

    @property
    def url(self):
        return reverse('cvterm-detail', kwargs={'pk': self.cvterm_id})


class Taxa(models.Model):
    taxa_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    rank = models.ForeignKey(Cvterm)

    class Meta:
        db_table = 'vavilov_taxa'


class TaxaRelationship(models.Model):
    taxa_relationship_id = models.AutoField(primary_key=True)
    taxa_subject = models.ForeignKey(Taxa, related_name='taxa_subject')
    taxa_object = models.ForeignKey(Taxa, related_name='taxa_object')
    type = models.ForeignKey(Cvterm)

    class Meta:
        db_table = 'vavilov_taxa_relationship'
        unique_together = ('taxa_subject', 'taxa_object', 'type')


class Person(models.Model):
    person_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=255, null=True)
    type = models.ForeignKey(Cvterm)  # is Lab, person,...

    class Meta:
        db_table = 'vavilov_person'

    def __str__(self):
        if self.description:
            return '{}({})'.format(self.description, self.name)
        else:
            return self.name


class PersonRelationship(models.Model):
    person_relationship_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Person, related_name='subject')
    object = models.ForeignKey(Person, related_name='object')
    type = models.ForeignKey(Cvterm)

    class Meta:
        db_table = 'vavilov_contact_relationship'


class Pub(models.Model):
    pub_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'vavilov_pub'


class Accession(models.Model):
    accession_id = models.AutoField(primary_key=True)

    accession_number = models.CharField(max_length=40,
                                        verbose_name='Accession number')  # BGV000094
    institute = models.ForeignKey(Person,
                                  verbose_name='Institute_code')  # COMAV
    type = models.ForeignKey(Cvterm, null=True)
    dbxref = models.ForeignKey(Dbxref, null=True)

    class Meta:
        db_table = 'vavilov_accession'
        permissions = (('view_accession', 'View Accession'),)

    def __str__(self):
        return '{}: {}'.format(self.institute, self.accession_number)

    @property
    def url(self):
        if self.dbxref:
            urlprefix = self.dbxref.db.urlprefix
            accession = self.dbxref.accession_name
            return '{}{}'.format(urlprefix, accession)

    @property
    def holder_accession(self):
        if self.institute.name == GENEBANK_CODE:
            equivalents = self.equivalent_accessions
            if equivalents:
                return equivalents[0]

    @property
    def equivalent_accessions(self):
        cv = Cv.objects.get(name='accession_relationship_types')
        is_relation = Cvterm.objects.get(cv=cv, name='is')

        return self._get_recursively_related_accessions([self], [is_relation],
                                                        symetric=True)

    @property
    def duplicated_accessions(self):
        cv = Cv.objects.get(name='accession_relationship_types')
        is_duplicated = Cvterm.objects.get(cv=cv, name='is_a_duplicated')
        equivalents = self.equivalent_accessions + [self]
        dup_accs = set()
        for equi_acc in equivalents:
            dup_accs.update(self._get_recursively_related_accessions([equi_acc],
                                                                     [is_duplicated],
                                                                     symetric=True))
        return list(dup_accs)

    @property
    def duplicated_accessions_and_equivalents(self):
        cv = Cv.objects.get(name='accession_relationship_types')
        is_duplicated = Cvterm.objects.get(cv=cv, name='is_a_duplicated')
        is_relation = Cvterm.objects.get(cv=cv, name='is')

        return self._get_recursively_related_accessions([self],
                                                        [is_duplicated, is_relation],
                                                        symetric=True)

    @property
    def donor_accession(self):
        equivalents = self.equivalent_accessions + [self]
        cv = Cv.objects.get(name='accession_relationship_types')
        is_duplicated_from = Cvterm.objects.get(cv=cv,
                                                name='is_duplicated_from')
        donor_accs = set()
        for equi_acc in equivalents:
            for acc_rel in AccessionRelationship.objects.filter(subject=equi_acc,
                                                                type=is_duplicated_from):
                donor_accs.add(acc_rel.object)

        if len(donor_accs) > 1:
            raise RuntimeError('DB relationship is broken. More than one doner for an accession')
        return list(donor_accs)[0] if donor_accs else None

    @property
    def collecting_accession(self):
        try:
            synonym = AccessionSynonym.objects.get(accession=self)
        except AccessionSynonym.DoesNotExist:
            return None
        return synonym.synonym_institute.name, synonym.synonym_code

    @property
    def collecting_number(self):
        collecting_accession = self.collecting_accession
        if collecting_accession:
            return collecting_accession[1]
        else:
            return None

    def _get_recursively_related_accessions(self, accessions, relations, symetric=True):
        if symetric:
            func = self._get_symetric_related_accessions
        else:
            func = self._get_non_symetric_related_accessions

        new_accessions = func(accessions, relations)
        while len(accessions) != len(new_accessions):
            new_accessions = self.func(accessions, relations)
            accessions = new_accessions
        return accessions[1:]

    def _get_symetric_related_accessions(self, accessions, relations):
        rel_query = reduce(operator.or_, [Q(type=relation) for relation in relations])
        for accession in accessions:
            subject_dups = AccessionRelationship.objects.filter(subject=accession)
            subject_dups = subject_dups.filter(rel_query)

            for subject_dup in subject_dups:
                dup_accession = subject_dup.object
                if dup_accession not in accessions:
                    accessions.append(dup_accession)

            object_dups = AccessionRelationship.objects.filter(object=accession)
            object_dups = object_dups.filter(rel_query)

            for object_dup in object_dups:
                dup_accession = object_dup.subject
                if dup_accession not in accessions:
                    accessions.append(dup_accession)

        return accessions

    def _get_non_symetric_related_accessions(self, accessions, relations):
        rel_query = reduce(operator.or_, [Q(type=relation) for relation in relations])
        for accession in accessions:
            subject_dups = AccessionRelationship.objects.filter(subject=accession)
            subject_dups = subject_dups.filter(rel_query)

            for subject_dup in subject_dups:
                dup_accession = subject_dup.object
                if dup_accession not in accessions:
                    accessions.append(dup_accession)
        return accessions

    @property
    def passport(self):
        equivalents = self.equivalent_accessions + [self]
        passport_datas = []
        for equi_acc in equivalents:
            try:
                passport_data = Passport.objects.get(accession=equi_acc)
            except Passport.DoesNotExist:
                passport_data = None

            if passport_data:
                passport_datas.append(passport_data)
        if len(passport_datas) == 0:
            return None
        elif len(passport_datas) == 1:
            return passport_datas[0]
        else:
            return ValueError('Equivalent accessions can not have more than one passport data')

    @property
    def collecting_country(self):
        try:
            return self.passport.location.country
        except AttributeError:
            return None

    @property
    def collecting_region(self):
        try:
            return self.passport.location.region
        except AttributeError:
            return None

    @property
    def collecting_province(self):
        try:
            return self.passport.location.province
        except AttributeError:
            return None

    @property
    def local_name(self):
        try:
            return self.passport.local_name
        except AttributeError:
            return None

    @property
    def collecting_date(self):
        try:
            return self.passport.collecting_date_str
        except AttributeError:
            return None

    @property
    def organism(self):
        accession_taxa = AccessionTaxa.objects.get(accession=self)
        taxon = accession_taxa.taxa
        if taxon.rank.name == 'Genus':
            return taxon.name + ' spp'
        organism = []

        for taxon in get_top_taxons(taxon)[::-1]:
            if taxon.rank.name not in ('Genus', 'Species'):
                name = ', {} {}'.format(taxon.rank.name, taxon.name)
            else:
                name = taxon.name
            organism.append(name)
        return ' '.join(organism)

    def plants(self, user):
        plants = Plant.objects.filter(accession=self)
        plants = get_objects_for_user(user, 'vavilov.view_plant',
                                      klass=plants, accept_global_perms=False)
        return plants

    def assays(self, user):
        assays = Assay.objects.filter(assayplant__plant__in=self.plants(user)).distinct()
        assays = get_objects_for_user(user, 'vavilov.view_assay',
                                      klass=assays, accept_global_perms=False)
        return assays

    def observations(self, user):
        obs = Observation.objects.filter(obs_entity__observationentityplant__plant__in=self.plants(user))
        obs = get_objects_for_user(user, 'vavilov.view_observation',
                                   klass=obs, accept_global_perms=False)
        return obs

    def obs_images(self, user):
        obs_images = ObservationImages.objects.filter(obs_entity__observationentityplant__plant__in=self.plants(user))
        obs_images = get_objects_for_user(user, 'vavilov.view_observation_images',
                                          klass=obs_images,
                                          accept_global_perms=False)
        return obs_images


def get_top_taxons(taxon):
    is_a = Cvterm.objects.get(cv__name='taxa_relationships', name='is_a')
    taxons = [taxon]
    while True:
        try:
            tax_rel = TaxaRelationship.objects.get(taxa_subject=taxon,
                                                   type=is_a)
        except TaxaRelationship.DoesNotExist:
            break
        taxon = tax_rel.taxa_object
        taxons.append(taxon)

    return taxons


def _get_bottom_taxons(taxons):
    is_a = Cvterm.objects.get(cv__name='taxa_relationships', name='is_a')
    for taxa in taxons:
        trs = TaxaRelationship.objects.filter(taxa_object=taxa, type=is_a)
        for tr in trs:
            taxa_subject = tr.taxa_subject
            if taxa_subject not in taxons:
                taxons.append(taxa_subject)
    return taxons


def get_bottom_taxons(taxons):
    while True:
        new_taxons = _get_bottom_taxons(taxons)
        if new_taxons == taxons:
            break
        taxons = new_taxons
    return taxons


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    site = models.CharField(max_length=255, null=True)  # COLLSITE
    province = models.CharField(max_length=255, null=True)
    region = models.CharField(db_index=True, max_length=255, null=True)
    country = models.ForeignKey(Country, null=True)  # ORIGCTY
    latitude = models.DecimalField(max_digits=9, decimal_places=4, null=True)  # LATITUDE
    longitude = models.DecimalField(max_digits=9, decimal_places=4, null=True)  # LONGITUDE
    altitude = models.IntegerField(null=True)  # ELEVATION

    class Meta:
        db_table = 'vavilov_location'
        permissions = (('view_location', 'View Location'),)

    @property
    def country_str(self):
        if self.country:
            return str(self.country)


class Passport(models.Model):
    passport_id = models.AutoField(primary_key=True)
    accession = models.ForeignKey(Accession)
    local_name = models.CharField(max_length=255, null=True)
    traditional_location = models.CharField(max_length=255, null=True)
    # location related_sites
    location = models.ForeignKey(Location, null=True)
    biological_status = models.ForeignKey(Cvterm, null=True,
                                          related_name='biological_status',
                                          verbose_name='Biological status of accession')  # SAMPSTAT
    collecting_source = models.ForeignKey(Cvterm, null=True,
                                          related_name='collecting_source',
                                          verbose_name='collecting_source')

    acquisition_date = models.DateField(null=True)
    collecting_date = models.DateField(null=True)
    # type = '

    class Meta:
        db_table = 'vavilov_passport'
        permissions = (('view_passport', 'View Passport'),)

    @property
    def data_to_show(self):
        data = OrderedDict()
        data['Local name'] = self.local_name
        data['Traditional location'] = self.traditional_location
        if self.location:
            data['Collecting site'] = self.location.site
            data['Collecting province'] = self.location.province
            data['Collecting region'] = self.location.region
            data['Collecting country'] = self.location.country_str
            data['Latitude'] = self.location.latitude
            data['Longitude'] = self.location.longitude
            data['Altitude'] = self.location.altitude
        else:
            data['Collecting site'] = None
            data['Collecting province'] = None
            data['Collecting region'] = None
            data['Collecting country'] = None
            data['Latitude'] = None
            data['Longitude'] = None
            data['Altitude'] = None
        data['Biological status'] = self.biological_status_str
        data['Collecting source'] = self.collecting_source_str
        data['Acquisition date'] = self.acquisition_date_str
        data['Collecting date'] = self.collecting_date_str

        return data

    @property
    def acquisition_date_str(self):
        return self.acquisition_date

    @property
    def collecting_date_str(self):
        return self.collecting_date

    @property
    def collecting_source_str(self):
        coll_source = self.collecting_source
        if coll_source:
            return '{} ({})'.format(coll_source.name, coll_source.definition)

    @property
    def biological_status_str(self):
        bio_stat = self.biological_status
        if bio_stat:
            return '{} ({})'.format(bio_stat.name, bio_stat.definition)

    @property
    def collecting_country(self):
        try:
            return self.location.country
        except AttributeError:
            return None


class AccessionProp(models.Model):
    accession_prop_id = models.AutoField(primary_key=True)
    accession = models.ForeignKey(Accession)
    type = models.ForeignKey(Cvterm)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'vavilov_accessionprop'


class AccessionTaxa(models.Model):
    accession_organism_id = models.AutoField(primary_key=True)
    accession = models.ForeignKey(Accession)
    taxa = models.ForeignKey(Taxa)
    creating_date = models.DateField(null=True)  # date when this relation was set
    author = models.ForeignKey(Person, null=True)
    pub = models.ForeignKey(Pub, null=True)

    class Meta:
        db_table = 'vavilov_accession_organism'
        unique_together = ('accession', 'taxa', 'creating_date')
        permissions = (('view_accessiontaxa', 'View Accession Taxa'),)


class AccessionRelationship(models.Model):
    accession_relationship_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Accession, related_name='subject')
    object = models.ForeignKey(Accession, related_name='object')
    type = models.ForeignKey(Cvterm)

    class Meta:
        db_table = 'vavilov_accession_relationship'
        permissions = (('view_accessionrelationship',
                        'View Accession Relationship'),)


class AccessionSynonym(models.Model):
    accession_synonym_id = models.AutoField(primary_key=True)
    accession = models.ForeignKey(Accession)
    synonym_institute = models.ForeignKey(Person)
    synonym_code = models.CharField(max_length=255)
    type = models.ForeignKey(Cvterm, null=True)

    class Meta:
        db_table = 'vavilov_accession_synonym'


class Assay(models.Model):
    # entity that groups a serie of observations given a set of plants and traits
    assay_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    year = models.CharField(max_length=255, null=True)
    location = models.ForeignKey(Location, null=True)
    owner = models.ForeignKey(User, null=True)

    class Meta:
        db_table = 'vavilov_assay'
        permissions = (('view_assay', 'View Assay'),)

    def __str__(self):
        return self.name

    def traits(self, user):
        traits = Trait.objects.filter(assaytrait__assay=self)
        return get_objects_for_user(user, 'vavilov.view_trait',
                                    klass=traits, accept_global_perms=False)

    @property
    def props(self):
        props_ = {}
        for assay_prop in AssayProp.objects.filter(assay=self):
            props_[assay_prop.type.name] = assay_prop.value
        return props_

    @property
    def get_absolute_url(self):
        return reverse('assay_view', kwargs={'name': self.name})

    def plants(self, user):
        plants = Plant.objects.filter(assayplant__assay=self).distinct()
        plants = get_objects_for_user(user, 'vavilov.view_plant',
                                      klass=plants, accept_global_perms=False)
        return plants

    def observations(self, user):
        obs = Observation.objects.filter(assay=self)
        obs = get_objects_for_user(user, 'vavilov.view_observation',
                                   klass=obs, accept_global_perms=False)
        return obs

    def obs_images(self, user):
        obs_images = ObservationImages.objects.filter(assay=self)
        obs_images = get_objects_for_user(user, 'vavilov.view_observation_images',
                                          klass=obs_images,
                                          accept_global_perms=False)
        return obs_images


class AssayProp(models.Model):
    assay_prop_id = models.AutoField(primary_key=True)
    assay = models.ForeignKey(Assay)
    type = models.ForeignKey(Cvterm)
    value = models.TextField()

#     start_date = models.DateField(null=True)
#     end_date = models.DateField(null=True)
#     location = models.CharField(max_length=255, null=True)
    class Meta:
        db_table = 'vavilov_assayprop'
        unique_together = ('assay', 'type')
        permissions = (('view_assayprop', 'View AssayProp'),)


class Plant(models.Model):
    plant_id = models.AutoField(primary_key=True)
    accession = models.ForeignKey(Accession)
    plant_name = models.CharField(max_length=255, unique=True)
    experimental_field = models.CharField(max_length=255, null=True)
    row = models.CharField(max_length=10, null=True)
    column = models.CharField(max_length=10, null=True)
    pot_number = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'vavilov_plant'
        permissions = (('view_plant', 'View Plant'),)

    def __str__(self):
        return self.plant_name

    def get_absolute_url(self):
        return reverse('plant_view', kwargs={'plant_name': self.plant_name})

    def assays(self, user):
        assays = Assay.objects.filter(assayplant__plant=self).distinct()
        assays = get_objects_for_user(user, 'vavilov.view_assay',
                                      klass=assays, accept_global_perms=False)
        return assays

    def observations(self, user):
        obs = Observation.objects.filter(obs_entity__observationentityplant__plant=self)
        obs = get_objects_for_user(user, 'vavilov.view_observation',
                                   klass=obs, accept_global_perms=False)

        return obs

    def obs_images(self, user):
        obs_images = ObservationImages.objects.filter(obs_entity__observationentityplant__plant=self)
        obs_images = get_objects_for_user(user, 'vavilov.view_observation_images',
                                          klass=obs_images,
                                          accept_global_perms=False)
        return obs_images


class AssayPlant(models.Model):
    assay_plant_id = models.AutoField(primary_key=True)
    assay = models.ForeignKey(Assay)
    plant = models.ForeignKey(Plant)

    class Meta:
        db_table = 'vavilov_assay_plant'
        unique_together = ('assay', 'plant')


class Trait(models.Model):
    trait_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    type = models.ForeignKey(Cvterm)

    class Meta:
        db_table = 'vavilov_trait'
        permissions = (('view_trait', 'View Trait'),)

    def __str__(self):
        return self.name

    @property
    def get_absolute_url(self):
        return reverse('trait_view', kwargs={'trait_id': self.trait_id})

    def observations(self, user):
        obs = Observation.objects.filter(trait=self)
        obs = get_objects_for_user(user, 'vavilov.view_observation',
                                   klass=obs)
        return obs

    @property
    def description(self):
        try:
            return self.props['description']
        except KeyError:
            return None

    @property
    def props(self):
        return {props.type.name: props.value for props in TraitProp.objects.filter(trait=self)}

    @property
    def assays(self):
        return Assay.objects.filter(assaytrait__trait=self)


class AssayTrait(models.Model):
    assay_trait_id = models.AutoField(primary_key=True)
    assay = models.ForeignKey(Assay)
    trait = models.ForeignKey(Trait)

    class Meta:
        db_table = 'vavilov_assay_trait'
        unique_together = ('trait', 'assay')


class TraitProp(models.Model):
    trait_prop_id = models.AutoField(primary_key=True)
    trait = models.ForeignKey(Trait)
    type = models.ForeignKey(Cvterm)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'vavilov_trait_prop'
        unique_together = ('trait', 'type')


class ObservationEntity(models.Model):
    obs_entity_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    part = models.ForeignKey(Cvterm)

    class Meta:
        db_table = 'vavilov_observation_entity'
        permissions = (('view_obs_entity', 'View Observation entity'),)

    def plants(self, user):
        plants = Plant.objects.filter(observationentityplant__obs_entity=self)
        plants = get_objects_for_user(user, 'vavilov.view_plant',
                                      klass=plants, accept_global_perms=False)
        return plants

    def observations(self, user):
        obs = Observation.objects.filter(obs_entity=self)
        obs = get_objects_for_user(user, 'vavilov.view_observation',
                                   klass=obs, accept_global_perms=False)
        return obs

    def obs_images(self, user):
        obs = ObservationImages.objects.filter(obs_entity=self)
        obs = get_objects_for_user(user, 'vavilov.view_observation_images',
                                   klass=obs, accept_global_perms=False)
        return obs

    @property
    def accession(self):
        plant = Plant.objects.filter(observationentityplant__obs_entity=self).first()
        return plant.accession

    def __str__(self):
        return self.name


class ObservationEntityPlant(models.Model):
    plant_group_plant_id = models.AutoField(primary_key=True)
    obs_entity = models.ForeignKey(ObservationEntity)
    plant = models.ForeignKey(Plant)

    class Meta:
        db_table = 'vavilov_observation_entity_plant'


class Observation(models.Model):
    observation_id = models.AutoField(primary_key=True)
    obs_entity = models.ForeignKey(ObservationEntity)
    assay = models.ForeignKey(Assay)
    trait = models.ForeignKey(Trait)
    value = models.TextField()
    creation_time = models.DateTimeField(null=True)
    observer = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'vavilov_observation'
        permissions = (('view_observation', 'View Observation'),)

    @property
    def plant(self):
        return self.plant_part.plant

    @property
    def accession(self):
        return self.obs_entity.accession


def get_photo_dir(instance, filename):
    # photo_dir/accession/imagename
    accession = instance.obs_entity.accession.accession_number
    plant_part = instance.obs_entity.part.name
    return '{}/{}/{}/{}'.format(PHENO_PHOTO_DIR, accession, plant_part,
                                filename)


def get_thumb_dir(instance, filename):
    # photo_dir/accession/thumbnails/imagename
    accession = instance.obs_entity.accession.accession_number
    plant_part = instance.obs_entity.part.name
    return '{}/{}/{}/thumbnails/{}'.format(PHENO_PHOTO_DIR, accession,
                                           plant_part, filename)

only_scan_storage = OnlyScanStorage(location=settings.MEDIA_ROOT,
                                    base_url=settings.MEDIA_URL)


class ObservationImages(models.Model):
    observation_image_id = models.AutoField(primary_key=True)
    observation_image_uid = models.CharField(max_length=255, unique=True)
    obs_entity = models.ForeignKey(ObservationEntity)
    assay = models.ForeignKey(Assay)
    trait = models.ForeignKey(Trait)
    image = models.ImageField(max_length=255, storage=only_scan_storage,
                              upload_to=get_photo_dir)
    thumbnail = models.ImageField(max_length=255, storage=only_scan_storage,
                                  null=True, blank=True,
                                  upload_to=get_thumb_dir)
    creation_time = models.DateTimeField()
    user = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'vavilov_observation_image'
        permissions = (('view_observation_images', 'View observation images'),)

    @property
    def plants(self):
        return self.obs_entity.plant_part.plant
