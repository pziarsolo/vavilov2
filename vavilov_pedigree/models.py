from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

FATHER = 'father'
MOTHER = 'mother'


class Accession(models.Model):
    accession_id = models.AutoField(primary_key=True)
    accession_number = models.CharField(max_length=255)
    collecting_number = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'vavilov_pedigree_accession'

    def __str__(self):
        return self.accession_number

    def get_absolute_url(self):
        return reverse('pedigree:accession-detail',
                       kwargs={'accession_number': self.accession_number})

    @property
    def seed_lots(self):
        return SeedLot.objects.filter(accession=self)

    @property
    def seed_lots_beauty(self):
        return ','.join([s.make_link_tag() for s in self.seed_lots])

    def make_link_tag(self):
        return mark_safe("<a href='{url}'>{visual}</a>".format(url=self.get_absolute_url(),
                                                               visual=self.accession_number))



class Assay(models.Model):
    assay_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'vavilov_pedigree_assay'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pedigree:assay-detail', kwargs={'name': self.name})

    @property
    def cross_experiments(self):
        return CrossExperiment.objects.filter(assay=self)


class SeedLot(models.Model):
    seed_lot_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, null=True)
    accession = models.ForeignKey(Accession)
    seeds_weight = models.FloatField(null=True)
    fruit = models.CharField(null=True, max_length=10)

    class Meta:
        db_table = 'vavilov_pedigree_seed_lot'

    def get_absolute_url(self):
        return reverse('pedigree:seedlot-detail', kwargs={'name': self.name})

    def __str__(self):
        return self.name

    def _parent(self, type_):
        try:
            cross = CrossExperiment.objects.get(crossexperimentseedlot__seed_lot=self)
            return getattr(cross, type_)
        except CrossExperiment.DoesNotExist:
            return None

    @property
    def mothers(self):
        return self._parent(type_='mothers')

    @property
    def fathers(self):
        return self._parent(type_='fathers')

    def make_link_tag(self):
        return mark_safe("<a href='{url}'>{visual}</a>".format(url=self.get_absolute_url(),
                                                               visual=self.name))

    def _parent_beauty(self, type_):
        parents = self._parent(type_=type_)
        accessions = set([p.seed_lot.accession.make_link_tag() for p in parents])
        accessions_beauty = " (" + ",".join(accessions) + ")"
        if len(self.mothers) == 1:
            return parents[0].make_link_tag() + accessions_beauty
        else:
            return 'various' + accessions_beauty

    @property
    def father_beauty(self):
        return self._parent_beauty('fathers')

    @property
    def mother_beauty(self):
        return  self._parent_beauty('mothers')

class Plant(models.Model):
    plant_id = models.AutoField(primary_key=True)
    plant_name = models.CharField(max_length=255)
    seed_lot = models.ForeignKey(SeedLot)
    experimental_field = models.CharField(max_length=255, null=True)
    row = models.CharField(max_length=10, null=True)
    column = models.CharField(max_length=10, null=True)
    pot_number = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = 'vavilov_pedigree_plant'

    def __str__(self):
        return self.plant_name

    def get_absolute_url(self):
        return reverse('pedigree:plant-detail', kwargs={'plant_name': self.plant_name})

    def make_link_tag(self):
        return mark_safe("<a href='{url}'>{visual}</a>".format(url=self.get_absolute_url(),
                                                               visual=self.plant_name))
    @property
    def clones(self):
        return self._get_recursively_related_accessions([self])

    def _get_recursively_related_accessions(self, plants):
        new_plants = self._get_symetric_related_accessions(plants)

        while len(plants) != len(new_plants):
            new_plants = self.func(plants)
            plants = new_plants
        return plants[1:]

    def _get_symetric_related_accessions(self, plants):
        for plant in plants:
            subject_rels = PlantRelationship.objects.filter(subject=plant)

            for subject_rel in subject_rels:
                clone = subject_rel.object
                if clone not in plants:
                    plants.append(clone)

            object_rels = PlantRelationship.objects.filter(object=plant)

            for object_rel in object_rels:
                clone = object_rel.subject
                if clone not in plants:
                    plants.append(clone)
        return plants


class PlantRelationship(models.Model):
    plant_relationship_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Plant, related_name='subject')
    object = models.ForeignKey(Plant, related_name='object')
    type = models.CharField(max_length=100, default='is_clone')

    class Meta:
        db_table = 'vavilov_pedigree_plant_relationshp'


class CrossExperiment(models.Model):
    cross_experiment_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, unique=True)
    assay = models.ForeignKey(Assay)

    class Meta:
        db_table = 'vavilov_pedigree_cross_experiment'

    def __str__(self):
        return self.description

    def _parents(self, type_):
        return Plant.objects.filter(Q(crossplant__cross=self) &
                             Q(crossplant__type=type_))
    @property
    def fathers(self):
        return self._parents(FATHER)

    @property
    def mothers(self):
        return self._parents(MOTHER)

    @property
    def offspring(self):
        return SeedLot.objects.filter(crossexperimentseedlot__cross_experiment=self)

    @property
    def offspring_beauty(self):
        offs_beauties = []
        for offspring in self.offspring:
            acc = offspring.accession.make_link_tag()
            offs_beauties.append('{} ({})'.format(offspring.make_link_tag(), acc))
        return ",".join(offs_beauties)

    def _parent_beauty(self, type_):
        parents = self._parents(type_=type_)
        accessions = set([p.seed_lot.accession.make_link_tag() for p in parents])
        accessions_beauty = " (" + ",".join(accessions) + ")"
        if len(parents) == 1:
            return parents[0].make_link_tag() + accessions_beauty
        else:
            return 'various' + accessions_beauty

    @property
    def father_beauty(self):
        return self._parent_beauty(FATHER)

    @property
    def mother_beauty(self):
        return  self._parent_beauty(MOTHER)


class CrossPlant(models.Model):
    cross_plant_id = models.AutoField(primary_key=True)
    cross = models.ForeignKey(CrossExperiment)
    plant = models.ForeignKey(Plant)
    type = models.CharField(max_length=10)

    class Meta:
        db_table = 'vavilov_pedigree_cross_plant'


class CrossExperimentSeedLot(models.Model):
    cross_experiment_seed_lot_id = models.AutoField(primary_key=True)
    cross_experiment = models.ForeignKey(CrossExperiment)
    seed_lot = models.OneToOneField(SeedLot)

    class Meta:
        db_table = 'vavilov_pedigree_cross_experiment_seed_lot'
