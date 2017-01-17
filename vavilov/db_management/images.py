import datetime
import os

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from guardian.shortcuts import assign_perm

from imagetools.exif import get_exif_comments, get_exif_metadata
from imagetools.utils import get_image_format, get_all_image_fpaths
from vavilov.conf.settings import OUR_TIMEZONE
from vavilov.db_management.phenotype import suggest_obs_entity_name
from vavilov.models import (Plant, Assay, Trait, ObservationImages,
                            Accession, Cvterm, ObservationEntity,
                            ObservationEntityPlant, Observation)


PLANT_PART = 'plant_part'
MAGIC_NUMBERS_BY_FORMAT = {'jpg': [b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xDB',
                                   b'\xFF\xD8\xFF\xE1'],
                           'bmp': [b'\x42\x4D'],
                           'gif': [b'\x47\x49\x46\x38\x39\x61',
                                   b'\x47\x49\x46\x38\x37\x61'],
                           'png': [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A']}


def get_thumbnail_path(photo_path, image_format):
    photo_dir, fname = os.path.split(photo_path)
    thumbnail_dir = os.path.join(photo_dir, 'thumbnails')
    return os.path.join(thumbnail_dir, fname)


def add_or_load_image_to_db(image_fpath, view_perm_group=None,
                            create_plant=False,
                            use_image_id_as_plant_id=False):
    image_format = get_image_format(image_fpath)
    thumb_fpath = get_thumbnail_path(image_fpath, image_format)

    exif = get_exif_metadata(image_fpath)
    try:
        creation_time = exif.get_date_time()
        creation_time = OUR_TIMEZONE.localize(creation_time, is_dst=True)
    except (KeyError, ValueError):
        creation_time = datetime.datetime.now()
        creation_time = OUR_TIMEZONE.localize(creation_time, is_dst=True)

    exif_data = get_exif_comments(image_fpath)
    try:
        image_id = exif_data['image_id']
    except KeyError:
        msg = 'This image does not have image_id in metadata comments: {}'
        raise RuntimeError(msg.format(image_fpath))

    try:
        obs_image = ObservationImages.objects.get(observation_image_uid=image_id)
        return obs_image
    except ObservationImages.DoesNotExist:
        pass

    try:
        plant_id = exif_data['plant_id']
    except KeyError:
        if use_image_id_as_plant_id:
            plant_id = image_id
        else:
            raise ValueError('plant info not in exif')

    try:
        assay = exif_data['assay']
    except KeyError:
        raise ValueError('Assay information not in exif')

    try:
        assay = Assay.objects.get(name=assay)
    except Assay.DoesNotExist:
        raise ValueError('Assay not loaded to db yet: {}'.format(assay))

    if view_perm_group is None:
        view_perm_group = assay.name
    group = Group.objects.get(name=view_perm_group)

    if create_plant:
        try:
            accession = Accession.objects.get(accession_number=exif_data['accession'])
        except Accession.DoesNotExist:
            print(exif_data['accession'], image_fpath)
            return
        plant = Plant.objects.get_or_create(accession=accession,
                                            plant_name=plant_id)[0]
        assign_perm('view_plant', group, plant)
    else:
        try:
            plant = Plant.objects.get(plant_name=plant_id)
        except Plant.DoesNotExist:
            raise ValueError('Plant from image not loaded to db yet: {}'.format(plant_id))

    part_name = exif_data[PLANT_PART].lower()
    part_type = Cvterm.objects.get(cv__name='plant_parts', name=part_name)

    obs_entity_name = suggest_obs_entity_name(plant_id, part_name)
    obs_entity, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                  part=part_type)
    if created:
        assign_perm('vavilov.view_obs_entity', group, obs_entity)
        ObservationEntityPlant.objects.create(obs_entity=obs_entity,
                                              plant=plant)

    trait_name = 'image_{}'.format(part_name)

    try:
        trait = Trait.objects.get(name=trait_name, assaytrait__assay=assay)
    except Trait.DoesNotExist:
        msg = 'Trait not loaded to db yet: {}, assay {}'
        raise ValueError(msg.format(trait_name, assay))

    observation = Observation.objects.create(obs_entity=obs_entity,
                                             assay=assay,
                                             trait=trait,
                                             creation_time=creation_time)
    assign_perm('vavilov.view_observation', group, observation)
    content_type = 'image/{}'.format(image_format)

    image_suf = SimpleUploadedFile(os.path.basename(image_fpath),
                                   open(image_fpath, 'rb').read(),
                                   content_type=content_type)

    thumb_suf = SimpleUploadedFile(os.path.basename(thumb_fpath),
                                   open(thumb_fpath, 'rb').read(),
                                   content_type=content_type)
    obs_image = ObservationImages.objects.create(observation=observation,
                                                 observation_image_uid=image_id,
                                                 image=image_suf,
                                                 thumbnail=thumb_suf)

    assign_perm('vavilov.view_observation_images', group, obs_image)

    return obs_image


def add_or_load_images(pheno_photo_dir, view_perm_group=None,
                       create_plant=False, use_image_id_as_plant_id=False):
    for image_path in get_all_image_fpaths(pheno_photo_dir, thumbnails=False):
        add_or_load_image_to_db(image_path, view_perm_group=view_perm_group,
                                create_plant=create_plant,
                                use_image_id_as_plant_id=use_image_id_as_plant_id)
