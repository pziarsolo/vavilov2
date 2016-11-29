# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import vavilov.utils.storage
import vavilov.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('accession_id', models.AutoField(serialize=False, primary_key=True)),
                ('accession_number', models.CharField(verbose_name='Accession number', max_length=40)),
            ],
            options={
                'db_table': 'vavilov_accession',
                'permissions': (('view_accession', 'View Accession'),),
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
                'db_table': 'vavilov_accessionprop',
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
                'db_table': 'vavilov_accession_relationship',
                'permissions': (('view_accessionrelationship', 'View Accession Relationship'),),
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
                'db_table': 'vavilov_accession_synonym',
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
                'db_table': 'vavilov_accession_organism',
                'permissions': (('view_accessiontaxa', 'View Accession Taxa'),),
            },
        ),
        migrations.CreateModel(
            name='Assay',
            fields=[
                ('assay_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.CharField(null=True, max_length=255)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('year', models.CharField(null=True, max_length=255)),
            ],
            options={
                'db_table': 'vavilov_assay',
                'permissions': (('view_assay', 'View Assay'),),
            },
        ),
        migrations.CreateModel(
            name='AssayPlant',
            fields=[
                ('assay_plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'db_table': 'vavilov_assay_plant',
            },
        ),
        migrations.CreateModel(
            name='AssayProp',
            fields=[
                ('assay_prop_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'db_table': 'vavilov_assayprop',
                'permissions': (('view_assayprop', 'View AssayProp'),),
            },
        ),
        migrations.CreateModel(
            name='AssayTrait',
            fields=[
                ('assay_trait_id', models.AutoField(serialize=False, primary_key=True)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'db_table': 'vavilov_assay_trait',
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
                'db_table': 'vavilov_country',
            },
        ),
        migrations.CreateModel(
            name='Cv',
            fields=[
                ('cv_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=48)),
                ('description', models.CharField(null=True, max_length=255)),
            ],
            options={
                'db_table': 'vavilov_cv',
            },
        ),
        migrations.CreateModel(
            name='Cvterm',
            fields=[
                ('cvterm_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('definition', models.CharField(null=True, max_length=255)),
                ('cv', models.ForeignKey(to='vavilov.Cv')),
            ],
            options={
                'db_table': 'vavilov_cvterm',
            },
        ),
        migrations.CreateModel(
            name='Db',
            fields=[
                ('db_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=48)),
                ('description', models.CharField(null=True, max_length=255)),
                ('urlprefix', models.CharField(null=True, max_length=255)),
                ('url', models.CharField(null=True, max_length=255)),
            ],
            options={
                'db_table': 'vavilov_db',
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
                'db_table': 'vavilov_dbxref',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('location_id', models.AutoField(serialize=False, primary_key=True)),
                ('site', models.CharField(null=True, max_length=255)),
                ('province', models.CharField(null=True, max_length=255)),
                ('region', models.CharField(null=True, max_length=255)),
                ('latitude', models.DecimalField(null=True, max_digits=9, decimal_places=4)),
                ('longitude', models.DecimalField(null=True, max_digits=9, decimal_places=4)),
                ('altitude', models.IntegerField(null=True)),
                ('country', models.ForeignKey(null=True, to='vavilov.Country')),
            ],
            options={
                'db_table': 'vavilov_location',
                'permissions': (('view_location', 'View Location'),),
            },
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('observation_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('creation_time', models.DateTimeField(null=True)),
                ('observer', models.CharField(null=True, max_length=255)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
            ],
            options={
                'db_table': 'vavilov_observation',
                'permissions': (('view_observation', 'View Observation'),),
            },
        ),
        migrations.CreateModel(
            name='ObservationEntity',
            fields=[
                ('obs_entity_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('part', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'vavilov_observation_entity',
                'permissions': (('view_obs_entity', 'View Observation entity'),),
            },
        ),
        migrations.CreateModel(
            name='ObservationEntityPlant',
            fields=[
                ('plant_group_plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('obs_entity', models.ForeignKey(to='vavilov.ObservationEntity')),
            ],
            options={
                'db_table': 'vavilov_observation_entity_plant',
            },
        ),
        migrations.CreateModel(
            name='ObservationImages',
            fields=[
                ('observation_image_id', models.AutoField(serialize=False, primary_key=True)),
                ('observation_image_uid', models.CharField(unique=True, max_length=255)),
                ('image', models.ImageField(storage=vavilov.utils.storage.OnlyScanStorage(location='/home/peio/devel/pyenv3/vavilov_dev/vavilov_web/media', base_url='/media/'), upload_to=vavilov.models.get_photo_dir, max_length=255)),
                ('thumbnail', models.ImageField(blank=True, null=True, storage=vavilov.utils.storage.OnlyScanStorage(location='/home/peio/devel/pyenv3/vavilov_dev/vavilov_web/media', base_url='/media/'), upload_to=vavilov.models.get_thumb_dir, max_length=255)),
                ('creation_time', models.DateTimeField()),
                ('user', models.CharField(null=True, max_length=255)),
                ('assay', models.ForeignKey(to='vavilov.Assay')),
                ('obs_entity', models.ForeignKey(to='vavilov.ObservationEntity')),
            ],
            options={
                'db_table': 'vavilov_observation_image',
                'permissions': (('view_observation_images', 'View observation images'),),
            },
        ),
        migrations.CreateModel(
            name='Passport',
            fields=[
                ('passport_id', models.AutoField(serialize=False, primary_key=True)),
                ('local_name', models.CharField(null=True, max_length=255)),
                ('traditional_location', models.CharField(null=True, max_length=255)),
                ('acquisition_date', models.DateField(null=True)),
                ('collecting_date', models.DateField(null=True)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
                ('biological_status', models.ForeignKey(null=True, to='vavilov.Cvterm', related_name='biological_status', verbose_name='Biological status of accession')),
                ('collecting_source', models.ForeignKey(null=True, to='vavilov.Cvterm', related_name='collecting_source', verbose_name='collecting_source')),
                ('location', models.ForeignKey(null=True, to='vavilov.Location')),
            ],
            options={
                'db_table': 'vavilov_passport',
                'permissions': (('view_passport', 'View Passport'),),
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('person_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=40)),
                ('description', models.CharField(null=True, max_length=255)),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'vavilov_person',
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
                'db_table': 'vavilov_contact_relationship',
            },
        ),
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('plant_name', models.CharField(unique=True, max_length=255)),
                ('experimental_field', models.CharField(null=True, max_length=255)),
                ('row', models.CharField(null=True, max_length=10)),
                ('column', models.CharField(null=True, max_length=10)),
                ('pot_number', models.CharField(null=True, max_length=10)),
                ('accession', models.ForeignKey(to='vavilov.Accession')),
            ],
            options={
                'db_table': 'vavilov_plant',
                'permissions': (('view_plant', 'View Plant'),),
            },
        ),
        migrations.CreateModel(
            name='Pub',
            fields=[
                ('pub_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'vavilov_pub',
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
                'db_table': 'vavilov_taxa',
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
                'db_table': 'vavilov_taxa_relationship',
            },
        ),
        migrations.CreateModel(
            name='Trait',
            fields=[
                ('trait_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'vavilov_trait',
                'permissions': (('view_trait', 'View Trait'),),
            },
        ),
        migrations.CreateModel(
            name='TraitProp',
            fields=[
                ('trait_prop_id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.CharField(max_length=255)),
                ('trait', models.ForeignKey(to='vavilov.Trait')),
                ('type', models.ForeignKey(to='vavilov.Cvterm')),
            ],
            options={
                'db_table': 'vavilov_trait_prop',
            },
        ),
        migrations.AddField(
            model_name='observationimages',
            name='trait',
            field=models.ForeignKey(to='vavilov.Trait'),
        ),
        migrations.AddField(
            model_name='observationentityplant',
            name='plant',
            field=models.ForeignKey(to='vavilov.Plant'),
        ),
        migrations.AddField(
            model_name='observation',
            name='obs_entity',
            field=models.ForeignKey(to='vavilov.ObservationEntity'),
        ),
        migrations.AddField(
            model_name='observation',
            name='trait',
            field=models.ForeignKey(to='vavilov.Trait'),
        ),
        migrations.AddField(
            model_name='cvterm',
            name='dbxref',
            field=models.ForeignKey(null=True, to='vavilov.Dbxref'),
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
            field=models.ForeignKey(null=True, to='vavilov.Location'),
        ),
        migrations.AddField(
            model_name='assay',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accessiontaxa',
            name='author',
            field=models.ForeignKey(null=True, to='vavilov.Person'),
        ),
        migrations.AddField(
            model_name='accessiontaxa',
            name='pub',
            field=models.ForeignKey(null=True, to='vavilov.Pub'),
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
            field=models.ForeignKey(null=True, to='vavilov.Cvterm'),
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
            field=models.ForeignKey(null=True, to='vavilov.Dbxref'),
        ),
        migrations.AddField(
            model_name='accession',
            name='institute',
            field=models.ForeignKey(to='vavilov.Person', verbose_name='Institute_code'),
        ),
        migrations.AddField(
            model_name='accession',
            name='type',
            field=models.ForeignKey(null=True, to='vavilov.Cvterm'),
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
