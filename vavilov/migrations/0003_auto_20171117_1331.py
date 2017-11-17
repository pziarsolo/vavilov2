# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-17 12:31
from __future__ import unicode_literals

from django.db import migrations, models
import vavilov.models
import vavilov.utils.storage


class Migration(migrations.Migration):

    dependencies = [
        ('vavilov', '0002_auto_20171113_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='plant',
            name='seed_lot',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='observationimages',
            name='image',
            field=models.ImageField(max_length=255, storage=vavilov.utils.storage.OnlyScanStorage(base_url='/media/', location='/home/peio/devel/pyenv3/vavilov_dev/vavilov_web/media'), upload_to=vavilov.models.get_photo_dir),
        ),
        migrations.AlterField(
            model_name='observationimages',
            name='thumbnail',
            field=models.ImageField(blank=True, max_length=255, null=True, storage=vavilov.utils.storage.OnlyScanStorage(base_url='/media/', location='/home/peio/devel/pyenv3/vavilov_dev/vavilov_web/media'), upload_to=vavilov.models.get_thumb_dir),
        ),
    ]
