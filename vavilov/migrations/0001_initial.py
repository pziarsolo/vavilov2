# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import vavilov.models
from django.conf import settings
import vavilov.utils.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('accession_id', models.AutoField(serialize=False, primary_key=True)),
                ('accession_number', models.CharField(verbose_name='Accession number', max_length=20)),
            ],
            options={
                'permissions': (('view_accession', 'View Accession'),),
                'db_table': 'accession',
            },
        ),
        migrations.CreateModel(
            name='AccessionProp',
            fields=[
                ('accession_prop_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=255)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
            ],
            options={
                'db_table': 'accessionprop',
            },
        ),
        migrations.CreateModel(
            name='AccessionRelationship',
            fields=[
                ('accession_relationship_id', models.AutoField(serialize=False, primary_key=True)),
                ('object', models.ForeignKey(to='vavilov.Accession', related_name='object')),
                ('subject', models.ForeignKey(to='vavilov.Accession', related_name='subject')),
            ],
            options={
                'permissions': (('view_accessionrelationship', 'View Accession Relationship'),),
                'db_table': 'accession_relationship',
            },
        ),
        migrations.CreateModel(
            name='AccessionSynonym',
            fields=[
                ('accession_synonym_id', models.AutoField(serialize=False, primary_key=True)),
                ('synonym_code', models.CharField(max_length=255)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
            ],
            options={
                'db_table': 'accession_synonym',
            },
        ),
        migrations.CreateModel(
            name='AccessionTaxa',
            fields=[
                ('accession_organism_id', models.AutoField(serialize=False, primary_key=True)),
                ('creating_date', models.DateField(null=True)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
            ],
            options={
                'permissions': (('view_accessiontaxa', 'View Accession Taxa'),),
                'db_table': 'accession_organism',
            },
        ),
        migrations.CreateModel(
            name='Assay',
            fields=[
                ('assay_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('description', models.CharField(max_length=100, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('year', models.CharField(max_length=255, null=True)),
            ],
            options={
                'permissions': (('view_assay', 'View Assay'),),
                'db_table': 'assay',
            },
        ),
        migrations.CreateModel(
            name='AssayPlant',
            fields=[
                ('assay_plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'db_table': 'assay_plant',
            },
        ),
        migrations.CreateModel(
            name='AssayProp',
            fields=[
                ('assay_prop_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=255)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'permissions': (('view_assayprop', 'View AssayProp'),),
                'db_table': 'assayprop',
            },
        ),
        migrations.CreateModel(
            name='AssayTrait',
            fields=[
                ('assay_trait_id', models.AutoField(serialize=False, primary_key=True)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'db_table': 'assay_trait',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('country_id', models.AutoField(serialize=False, primary_key=True)),
                ('code2', models.CharField(max_length=2)),
                ('code3', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'country',
            },
        ),
        migrations.CreateModel(
            name='Cv',
            fields=[
                ('cv_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=48)),
                ('description', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'cv',
            },
        ),
        migrations.CreateModel(
            name='Cvterm',
            fields=[
                ('cvterm_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('definition', models.CharField(max_length=255, null=True)),
                ('cv', models.ForeignKey(to='vavilov.Cv')),
            ],
            options={
                'db_table': 'cvterm',
            },
        ),
        migrations.CreateModel(
            name='Db',
            fields=[
                ('db_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=48)),
                ('description', models.CharField(max_length=255, null=True)),
                ('urlprefix', models.CharField(max_length=255, null=True)),
                ('url', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'db',
            },
        ),
        migrations.CreateModel(
            name='Dbxref',
            fields=[
                ('dbxref_id', models.AutoField(serialize=False, primary_key=True)),
                ('accession_name', models.CharField(max_length=255)),
                ('db', models.ForeignKey(to='vavilov.Db')),
            ],
            options={
                'db_table': 'dbxref',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location_id', models.AutoField(serialize=False, primary_key=True)),
                ('site', models.CharField(max_length=50, null=True)),
                ('province', models.CharField(max_length=50, null=True)),
                ('region', models.CharField(max_length=50, null=True)),
                ('latitude', models.DecimalField(max_digits=9, null=True, decimal_places=4)),
                ('longitude', models.DecimalField(max_digits=9, null=True, decimal_places=4)),
                ('altitude', models.IntegerField(null=True)),
                ('country', models.ForeignKey(to='vavilov.Country', null=True)),
            ],
            options={
                'permissions': (('view_location', 'View Location'),),
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('observation_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=100)),
                ('creation_time', models.DateTimeField()),
                ('observer', models.CharField(max_length=100, null=True)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'permissions': (('view_observation', 'View Observation'),),
                'db_table': 'observation',
            },
        ),
        migrations.CreateModel(
            name='ObservationImages',
            fields=[
                ('observation_image_id', models.AutoField(serialize=False, primary_key=True)),
                ('observation_image_uid', models.CharField(unique=True, max_length=255)),
                ('image', models.ImageField(storage=vavilov.utils.storage.OnlyScanStorage(base_url='/media/', location='/'), max_length=255, upload_to=vavilov.models.get_photo_dir)),
                ('thumbnail', models.ImageField(max_length=255, blank=True, upload_to=vavilov.models.get_thumb_dir, null=True, storage=vavilov.utils.storage.OnlyScanStorage(base_url='/media/', location='/'))),
                ('creation_time', models.DateTimeField()),
                ('user', models.CharField(max_length=100, null=True)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'permissions': (('view_observation_images', 'View observation images'),),
                'db_table': 'observation_image',
            },
        ),
        migrations.CreateModel(
            name='Passport',
            fields=[
                ('passport_id', models.AutoField(serialize=False, primary_key=True)),
                ('local_name', models.CharField(max_length=50, null=True)),
                ('traditional_location', models.CharField(max_length=50, null=True)),
                ('acquisition_date', models.DateField(null=True)),
                ('collecting_date', models.DateField(null=True)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
                ('biological_status', models.ForeignKey(to='vavilov.Cvterm', related_name='biological_status', verbose_name='Biological status of accession', null=True)),
                ('collecting_source', models.ForeignKey(to='vavilov.Cvterm', related_name='collecting_source', verbose_name='collecting_source', null=True)),
                ('location', models.ForeignKey(to='vavilov.Location', null=True)),
            ],
            options={
                'permissions': (('view_passport', 'View Passport'),),
                'db_table': 'passport',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('person_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20)),
                ('description', models.CharField(max_length=255, null=True)),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'person',
            },
        ),
        migrations.CreateModel(
            name='PersonRelationship',
            fields=[
                ('person_relationship_id', models.AutoField(serialize=False, primary_key=True)),
                ('object', models.ForeignKey(to='vavilov.Person', related_name='object')),
                ('subject', models.ForeignKey(to='vavilov.Person', related_name='subject')),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'contact_relationship',
            },
        ),
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('plant_name', models.CharField(unique=True, max_length=100)),
                ('experimental_field', models.CharField(max_length=255, null=True)),
                ('row', models.CharField(max_length=10, null=True)),
                ('column', models.CharField(max_length=10, null=True)),
                ('pot_number', models.CharField(max_length=10, null=True)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
            ],
            options={
                'permissions': (('view_plant', 'View Plant'),),
                'db_table': 'plant',
            },
        ),
        migrations.CreateModel(
            name='PlantPart',
            fields=[
                ('plant_part_id', models.AutoField(serialize=False, primary_key=True)),
                ('plant_part_uid', models.CharField(unique=True, max_length=255)),
                ('part', models.ForeignKey(to='vavilov.Cvterm')),
                ('plant', models.ForeignKey(to='vavilov.Plant')),
            ],
            options={
                'db_table': 'plant_part',
            },
        ),
        migrations.CreateModel(
            name='Pub',
            fields=[
                ('pub_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'pub',
            },
        ),
        migrations.CreateModel(
            name='Taxa',
            fields=[
                ('taxa_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('rank', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'taxa',
            },
        ),
        migrations.CreateModel(
            name='TaxaRelationship',
            fields=[
                ('taxa_relationship_id', models.AutoField(serialize=False, primary_key=True)),
                ('taxa_object', models.ForeignKey(to='vavilov.Taxa', related_name='taxa_object')),
                ('taxa_subject', models.ForeignKey(to='vavilov.Taxa', related_name='taxa_subject')),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'taxa_relationship',
            },
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('trait_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'permissions': (('view_trait', 'View Trait'),),
                'db_table': 'trait',
            },
        ),
        migrations.CreateModel(
            name='TraitProp',
            fields=[
                ('trait_prop_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=100)),
                ('trait', models.ForeignKey(to='vavilov.Trait')),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'trait_prop',
            },
        ),
        migrations.AddField(
            model_name='observationimages',
            name='plant_part',
            field=models.ForeignKey(to='vavilov.PlantPart'),
        ),
        migrations.AddField(
            model_name='observationimages',
            name='trait',
            field=models.ForeignKey(to='vavilov.Trait'),
        ),
        migrations.AddField(
            model_name='observation',
            name='plant_part',
            field=models.ForeignKey(to='vavilov.PlantPart'),
        ),
        migrations.AddField(
            model_name='observation',
            name='trait',
            field=models.ForeignKey(to='vavilov.Trait'),
        ),
        migrations.AddField(
            model_name='cvterm',
            name='dbxref',
            field=models.ForeignKey(to='vavilov.Dbxref', null=True),
        ),
        migrations.AddField(
            model_name='assaytrait',
            name='trait',
            field=models.ForeignKey(to='vavilov.Trait'),
        ),
        migrations.AddField(
            model_name='assayprop',
            name='type',
            field=models.ForeignKey(to='vavilov.Cvterm'),
        ),
        migrations.AddField(
            model_name='assayplant',
            name='plant',
            field=models.ForeignKey(to='vavilov.Plant'),
        ),
        migrations.AddField(
            model_name='assay',
            name='location',
            field=models.ForeignKey(to='vavilov.Location', null=True),
        ),
        migrations.AddField(
            model_name='assay',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='accessiontaxa',
            name='author',
            field=models.ForeignKey(to='vavilov.Person', null=True),
        ),
        migrations.AddField(
            model_name='accessiontaxa',
            name='pub',
            field=models.ForeignKey(to='vavilov.Pub', null=True),
        ),
        migrations.AddField(
            model_name='accessiontaxa',
            name='taxa',
            field=models.ForeignKey(to='vavilov.Taxa'),
        ),
        migrations.AddField(
            model_name='accessionsynonym',
            name='synonym_institute',
            field=models.ForeignKey(to='vavilov.Person'),
        ),
        migrations.AddField(
            model_name='accessionsynonym',
            name='type',
            field=models.ForeignKey(to='vavilov.Cvterm', null=True),
        ),
        migrations.AddField(
            model_name='accessionrelationship',
            name='type',
            field=models.ForeignKey(to='vavilov.Cvterm'),
        ),
        migrations.AddField(
            model_name='accessionprop',
            name='type',
            field=models.ForeignKey(to='vavilov.Cvterm'),
        ),
        migrations.AddField(
            model_name='accession',
            name='dbxref',
            field=models.ForeignKey(to='vavilov.Dbxref', null=True),
        ),
        migrations.AddField(
            model_name='accession',
            name='institute',
            field=models.ForeignKey(to='vavilov.Person', verbose_name='Institute_code'),
        ),
        migrations.AddField(
            model_name='accession',
            name='type',
            field=models.ForeignKey(to='vavilov.Cvterm', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='traitprop',
            unique_together=set([('trait', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='taxarelationship',
            unique_together=set([('taxa_subject', 'taxa_object', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='dbxref',
            unique_together=set([('db', 'accession_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='cvterm',
            unique_together=set([('cv', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='assaytrait',
            unique_together=set([('trait', 'assay')]),
        ),
        migrations.AlterUniqueTogether(
            name='assayprop',
            unique_together=set([('assay', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='assayplant',
            unique_together=set([('assay', 'plant')]),
        ),
        migrations.AlterUniqueTogether(
            name='accessiontaxa',
            unique_together=set([('accession', 'taxa', 'creating_date')]),
        ),
    ]
