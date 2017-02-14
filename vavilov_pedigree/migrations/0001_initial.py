# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('accession_id', models.AutoField(serialize=False, primary_key=True)),
                ('accession_number', models.CharField(max_length=255)),
                ('collecting_number', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'vavilov_pedigree_accession',
            },
        ),
        migrations.CreateModel(
            name='Assay',
            fields=[
                ('assay_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'vavilov_pedigree_assay',
            },
        ),
        migrations.CreateModel(
            name='CrossExperiment',
            fields=[
                ('cross_experiment_id', models.AutoField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=255, unique=True)),
                ('assay', models.ForeignKey(to='vavilov_pedigree.Assay')),
            ],
            options={
                'db_table': 'vavilov_pedigree_cross_experiment',
            },
        ),
        migrations.CreateModel(
            name='CrossExperimentSeedLot',
            fields=[
                ('cross_experiment_seed_lot_id', models.AutoField(serialize=False, primary_key=True)),
                ('cross_experiment', models.ForeignKey(to='vavilov_pedigree.CrossExperiment')),
            ],
            options={
                'db_table': 'vavilov_pedigree_cross_experiment_seed_lot',
            },
        ),
        migrations.CreateModel(
            name='CrossPlant',
            fields=[
                ('cross_plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=10)),
                ('cross', models.ForeignKey(to='vavilov_pedigree.CrossExperiment')),
            ],
            options={
                'db_table': 'vavilov_pedigree_cross_plant',
            },
        ),
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('plant_id', models.AutoField(serialize=False, primary_key=True)),
                ('plant_name', models.CharField(max_length=255)),
                ('experimental_field', models.CharField(max_length=255, null=True)),
                ('row', models.CharField(max_length=10, null=True)),
                ('column', models.CharField(max_length=10, null=True)),
                ('pot_number', models.CharField(max_length=10, null=True)),
            ],
            options={
                'db_table': 'vavilov_pedigree_plant',
            },
        ),
        migrations.CreateModel(
            name='PlantRelationship',
            fields=[
                ('plant_relationship_id', models.AutoField(serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=100, default='is_clone')),
                ('object', models.ForeignKey(related_name='object', to='vavilov_pedigree.Plant')),
                ('subject', models.ForeignKey(related_name='subject', to='vavilov_pedigree.Plant')),
            ],
            options={
                'db_table': 'vavilov_pedigree_plant_relationshp',
            },
        ),
        migrations.CreateModel(
            name='SeedLot',
            fields=[
                ('seed_lot_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.CharField(max_length=255, null=True)),
                ('seeds_weight', models.FloatField(null=True)),
                ('fruit', models.CharField(max_length=10, null=True)),
                ('accession', models.ForeignKey(to='vavilov_pedigree.Accession')),
            ],
            options={
                'db_table': 'vavilov_pedigree_seed_lot',
            },
        ),
        migrations.AddField(
            model_name='plant',
            name='seed_lot',
            field=models.ForeignKey(to='vavilov_pedigree.SeedLot'),
        ),
        migrations.AddField(
            model_name='crossplant',
            name='plant',
            field=models.ForeignKey(to='vavilov_pedigree.Plant'),
        ),
        migrations.AddField(
            model_name='crossexperimentseedlot',
            name='seed_lot',
            field=models.OneToOneField(to='vavilov_pedigree.SeedLot'),
        ),
    ]
