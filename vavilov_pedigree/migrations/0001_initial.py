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
                ('accession_id', models.AutoField(primary_key=True, serialize=False)),
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
                ('assay_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'db_table': 'vavilov_pedigree_assay',
            },
        ),
        migrations.CreateModel(
            name='CrossExperiment',
            fields=[
                ('cross_experiment_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(unique=True, max_length=255)),
                ('assay', models.ForeignKey(to='vavilov_pedigree.Assay')),
            ],
            options={
                'db_table': 'vavilov_pedigree_cross_experiment',
            },
        ),
        migrations.CreateModel(
            name='CrossExperimentSeedLot',
            fields=[
                ('cross_experiment_seed_lot_id', models.AutoField(primary_key=True, serialize=False)),
                ('cross_experiment', models.ForeignKey(to='vavilov_pedigree.CrossExperiment')),
            ],
            options={
                'db_table': 'vavilov_pedigree_cross_experiment_seed_lot',
            },
        ),
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('plant_id', models.AutoField(primary_key=True, serialize=False)),
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
                ('plant_relationship_id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(default='is_clone', max_length=100)),
                ('object', models.ForeignKey(to='vavilov_pedigree.Plant', related_name='object')),
                ('subject', models.ForeignKey(to='vavilov_pedigree.Plant', related_name='subject')),
            ],
            options={
                'db_table': 'vavilov_pedigree_plant_relationshp',
            },
        ),
        migrations.CreateModel(
            name='SeedLot',
            fields=[
                ('seed_lot_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.CharField(max_length=255, null=True)),
                ('seeds_weight', models.FloatField(null=True)),
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
            model_name='crossexperimentseedlot',
            name='seed_lot',
            field=models.OneToOneField(to='vavilov_pedigree.SeedLot'),
        ),
        migrations.AddField(
            model_name='crossexperiment',
            name='father',
            field=models.ForeignKey(to='vavilov_pedigree.Plant', related_name='father'),
        ),
        migrations.AddField(
            model_name='crossexperiment',
            name='mother',
            field=models.ForeignKey(to='vavilov_pedigree.Plant', related_name='mother'),
        ),
    ]
