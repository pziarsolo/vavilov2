import csv
import datetime
import os
from random import Random
import sys
import json

from django.contrib.auth.models import User, Group
from django.db import transaction
from django.db.utils import DataError
from guardian.shortcuts import assign_perm

from vavilov.conf.settings import OUR_TIMEZONE
from vavilov.db_management.base import comma_dialect
from vavilov.db_management.excel import excel_dict_reader
from vavilov.models import (Observation, Trait, Assay, AssayPlant,
                            Cvterm, TraitProp, AssayTrait, AssayProp, Plant,
                            Accession, ObservationEntity,
                            ObservationEntityPlant, ObservationImages,
                            ObservationRelationship)

NOT_ALLOWED_VALUES = ('.',)
TRAIT_PROPS_CV = 'trait_props'
TRAIT_TYPES_CV = 'trait_types'

COLNUMBER_HEADER = 'CollectinCode'
ASSAY_HEADER = 'Assay'
PLANT_PART_HEADER = 'Plant_part'
PLANT_HEADER = 'Plant_name'
ACCESSION_HEADER = 'Accession'
PHOTO_HEADER = 'Photo id'


def add_or_load_assays(fpath):
    fhand = open(fpath)
    with transaction.atomic():
        for entry in csv.DictReader(fhand, dialect=comma_dialect):
            assay_data = {}
            props = {}
            for key, value in entry.items():
                if not value:
                    continue
                if key in ('name', 'description', 'start_date', 'end_date',
                           'location'):
                    assay_data[key] = value
                elif key == 'owner':
                    owner = value
                else:
                    props[key] = value

            try:
                owner = User.objects.get(username=owner)
            except User.DoesNotExist:
                msg = 'user {} owner of assay {} does not exist'
                raise RuntimeError(msg.format(owner, entry['name']))
            assay_data['owner'] = owner
            try:
                assay = Assay.objects.get(name=assay_data['name'])
            except Assay.DoesNotExist:
                assay = None

            if assay:
                continue

            assay = Assay.objects.create(**assay_data)

            for key, value in props.items():
                type_ = Cvterm.objects.get(cv__name='assay_props',
                                           name=key)
                AssayProp.objects.create(assay=assay, type=type_,
                                         value=value)
            group = Group.objects.get_or_create(name=assay.name)[0]
            assign_perm('view_assay', group, assay)
            group.user_set.add(owner)


def add_observation(obs_entity, trait_name, assay_name, value, creation_time,
                    observer=None, force=True):
    try:
        assay = Assay.objects.get(name=assay_name)
    except Assay.DoesNotExist:
        raise ValueError('Assay not loaded yet in db: {}'.format(assay_name))
    try:
        trait = Trait.objects.get(name=trait_name, assaytrait__assay=assay)
    except Trait.DoesNotExist:
        raise ValueError('Trait not loaded yet in db: {}:{}'.format(trait_name,
                                                                    assay_name))
    plants = Plant.objects.filter(observationentityplant__obs_entity=obs_entity)

    try:
        [AssayPlant.objects.filter(assay=assay, plant=p) for p in plants]
    except AssayPlant.DoesNotExist:
        msg = 'This assay {} and this plants {} are not related'
        msg = msg.format(assay, ','.join([p.plant_name for p in plants]))
        raise ValueError(msg)
    if value in (None, '') or value in NOT_ALLOWED_VALUES:
        msg = ' No value or value has not allowed characters:{} {} {}'
        msg = msg.format(obs_entity.accession.accession_number, assay.name,
                         trait.name)
        raise ValueError(msg)
    try:
        if force:
            obs = Observation.objects.create(obs_entity=obs_entity, trait=trait,
                                             assay=assay, value=value,
                                             creation_time=creation_time,
                                             observer=observer)
        else:
            obs = Observation.objects.get_or_create(obs_entity=obs_entity,
                                                    trait=trait, assay=assay,
                                                    value=value,
                                                    creation_time=creation_time,
                                                    observer=observer)[0]
    except DataError:
        print(value, observer)
        raise
    return obs


def add_or_load_excel_traits(fpath, assays):
    with transaction.atomic():
        for row in excel_dict_reader(fpath):
            name = row.pop('name')
            type_ = row.pop('type')
            #description = row.get('description', None)
            try:
                type_ = Cvterm.objects.get(name=type_, cv__name=TRAIT_TYPES_CV)
            except Cvterm.DoesNotExist:
                msg = 'Trait type not loaded yet in db: {}'.format(type_)
                raise RuntimeError(msg)

            trait, trait_created = Trait.objects.get_or_create(name=name, type=type_)
            for assay in assays:
                try:
                    assay = Assay.objects.get(name=assay)
                except Assay.DoesNotExist:
                    raise RuntimeError('Assay not loaded yet in db: {}'.format(assay))

                created = AssayTrait.objects.get_or_create(assay=assay,
                                                           trait=trait)[1]
                if created:
                    assign_perm('view_trait', assay.owner, trait)

            if trait_created:
                for prop, prop_value in row.items():
                    if not prop_value:
                        continue
                    try:
                        prop_type = Cvterm.objects.get(cv__name=TRAIT_PROPS_CV,
                                                       name=prop)
                    except Cvterm.DoesNotExist:
                        print('#{}#'.format(prop))
                        raise
                    try:
                        TraitProp.objects.create(trait=trait, type=prop_type,
                                                 value=prop_value)
                    except Exception:
                        print(trait.name, prop_type.name, prop_value)


def add_or_load_plants(fpath, assay, experimental_field_header=None,
                       row_header=None, column_header=None,
                       pot_number_header=None, view_perm_group=None):
    fhand = open(fpath)
    assay = Assay.objects.get(name=assay)
    if view_perm_group is None:
        view_perm_group = assay.name
    group = Group.objects.get(name=view_perm_group)
    with transaction.atomic():
        for entry in csv.DictReader(fhand, dialect=comma_dialect):
            plant_name = entry['plant_id']
            accession_code = entry['accession']

            exp_field = entry.get(experimental_field_header, None)
            row = entry.get(row_header, None)
            column = entry.get(column_header, None)
            pot_number = entry.get(pot_number_header, None)

            new_plant = False
            try:
                plant = Plant.objects.get(plant_name=plant_name)
            except Plant.DoesNotExist:
                new_plant = True

            if new_plant:
                try:
                    accession = Accession.objects.get(accession_number=accession_code)
                except BaseException:
                    print(accession_code)
                    raise

                plant = Plant.objects.create(plant_name=plant_name,
                                             accession=accession,
                                             experimental_field=exp_field,
                                             row=row, column=column,
                                             pot_number=pot_number)

                assign_perm('view_plant', group, plant)
            AssayPlant.objects.get_or_create(assay=assay, plant=plant)


class RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is six characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    characters = "abcdefghijklmnopqrstuvwxyz0123456789"

    @property
    def rng(self):
        cur_pid = os.getpid()
        if cur_pid != getattr(self, '_rng_pid', None):
            self._rng = Random()
            self._rng_pid = cur_pid
        return self._rng

    def __iter__(self):
        return self

    def __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) for dummy in range(8)]
        return ''.join(letters)


NAMER = RandomNameSequence()


def suggest_obs_entity_name(plant_name, plant_part):
    if plant_part == 'plant':
        return '{}_{}'.format(plant_name, plant_part)
    obs_ent_name = '{}_{}_{}'.format(plant_name, plant_part, next(NAMER))
    try:
        ObservationEntity.objects.get(name=obs_ent_name)
    except ObservationEntity.DoesNotExist:
        return obs_ent_name
    else:
        return suggest_obs_entity_name(plant_name, plant_part)


def get_or_create_obs_entity(accession_number, assay_name, plant_part,
                             plant_name=None, obs_entity_name=None,
                             plant_number=None, perm_gr=None,
                             one_part_per_plant=False, photo_uuid=None):
    try:
        plant_part_type = Cvterm.objects.get(cv__name='plant_parts',
                                             name=plant_part)
    except Cvterm.DoesNotExist:
        msg = '{} plant part not in cvterm table'.format(plant_part)
        raise ValueError(msg)

    try:
        accession = Accession.objects.get(accession_number=accession_number)
    except Accession.DoesNotExist:
        msg = '{} accession not in db'.format(accession_number)
        raise ValueError(msg)
    try:
        assay = Assay.objects.get(name=assay_name)
    except Assay.DoesNotExist:
        msg = '{} assay not in db'.format(assay_name)
        raise ValueError(msg)

    if obs_entity_name:
        # In this case, the obs_entity must be added already
        try:
            obs_ent = ObservationEntity.objects.get(name=obs_entity_name,
                                                    part=plant_part_type)
        except ObservationEntity.DoesNotExist:
            msg = '{} obs_entity'.format(obs_entity_name)
            raise ValueError(msg)

    elif photo_uuid:
        obs_entity_name = '{}_{}_{}'.format(plant_name, plant_part,
                                            photo_uuid)
        obs_ent, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                   part=plant_part_type)
        if created:
            assign_perm('view_obs_entity', perm_gr, obs_ent)
            plant, p_creat = Plant.objects.get_or_create(plant_name=plant_name,
                                                         accession=accession)
            ObservationEntityPlant.objects.get_or_create(obs_entity=obs_ent,
                                                         plant=plant)
            if p_creat:
                assign_perm('view_plant', perm_gr, plant)

                AssayPlant.objects.create(plant=plant, assay=assay)
    elif plant_name:
        if not one_part_per_plant:
            obs_entity_name = suggest_obs_entity_name(plant_name, plant_part)
        else:
            obs_entity_name = '{}_{}'.format(plant_name, plant_part)
        obs_ent, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                   part=plant_part_type)

        if created:
            assign_perm('view_obs_entity', perm_gr, obs_ent)
            plant, p_creat = Plant.objects.get_or_create(plant_name=plant_name,
                                                         accession=accession)
            ObservationEntityPlant.objects.get_or_create(obs_entity=obs_ent,
                                                         plant=plant)
            if p_creat:
                assign_perm('view_plant', perm_gr, plant)
                AssayPlant.objects.create(plant=plant, assay=assay)

    elif plant_number:
        obs_entity_name = '{}_{}_{}_{}'.format(accession.accession_number,
                                               assay.name, plant_part,
                                               plant_number)
        obs_ent, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                   part=plant_part_type)
        if created:
            assign_perm('view_obs_entity', perm_gr, obs_ent)
            plant_name = '{}_{}_{}'.format(accession.accession_number,
                                           assay.name, plant_number)
            plant, p_creat = Plant.objects.get_or_create(plant_name=plant_name,
                                                         accession=accession)
            ObservationEntityPlant.objects.get_or_create(obs_entity=obs_ent,
                                                         plant=plant)
            if p_creat:
                assign_perm('view_plant', perm_gr, plant)

                AssayPlant.objects.create(plant=plant, assay=assay)
    else:
        # hay que crear una obs entity con todas las plantas de este accession
        # en este ensayo

        obs_entity_name = '{}_{}_{}'.format(accession.accession_number,
                                            assay.name, plant_part)
        obs_ent, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                   part=plant_part_type)
        if created:
            assign_perm('view_obs_entity', perm_gr, obs_ent)
            plants = Plant.objects.filter(accession=accession,
                                          assayplant__assay=assay)
            if not plants:
                plant_name = obs_entity_name
                plant = Plant.objects.create(plant_name=plant_name,
                                             accession=accession)
                plants = [plant]
            for plant in plants:
                ObservationEntityPlant.objects.create(obs_entity=obs_ent,
                                                      plant=plant)

    return obs_ent


def parse_qual_translator(fhand):
    trait_values = {}
    for entry in csv.DictReader(fhand):
        trait = entry['name'].strip()
        score = entry['score'].strip()
        value = entry['value'].strip()
        if trait not in trait_values:
            trait_values[trait] = {}
        trait_values[trait][score] = value
    return trait_values


def add_excel_observations(fpath, observer=None, assay=None,
                           plant_part=None,
                           accession_header='accession',
                           value_header='value', date_header='Fecha',
                           observer_header='Autor',
                           assay_header='assay',
                           plant_part_header='plant_part',
                           obs_uid_header='part_uid',
                           plant_name_header='plant_name',
                           plant_number_header='plant_number',
                           trait_header='trait',
                           view_perm_group=None,
                           raise_on_error=True,
                           qualitative_translator=None):
    with transaction.atomic():
        for row in excel_dict_reader(fpath):
            value = row.get(value_header, None)
            if value is None or value == 'nd':
                continue

            plant_name = row.get(plant_name_header, None)
            plant_part = row.get(plant_part_header, plant_part)
            obs_entity_name = row.get(obs_uid_header, None)
            plant_number = row.get(plant_number_header, None)
            accession = row.get(accession_header, None)
            assayname = row.get(assay_header, assay)

            if view_perm_group is None:
                view_perm_group = assayname
            perm_gr = Group.objects.get(name=view_perm_group)
            try:
                obs_entity = get_or_create_obs_entity(accession_number=accession,
                                                      assay_name=assayname,
                                                      plant_part=plant_part,
                                                      plant_name=plant_name,
                                                      obs_entity_name=obs_entity_name,
                                                      plant_number=plant_number,
                                                      perm_gr=perm_gr)
            except ValueError as error:
                if raise_on_error:
                    raise
                else:
                    sys.stderr.write(str(error) + '\n')
                    continue

            creation_time = row.get(date_header)
            if creation_time is None:
                creation_time = datetime.datetime.now()
            creation_time = OUR_TIMEZONE.localize(creation_time, is_dst=True)

            observer = row.get(observer_header, observer)
            trait_name = row.get(trait_header)

            if qualitative_translator:
                try:
                    value = qualitative_translator[trait_name][str(value)]
                except KeyError as error:
                    if raise_on_error:
                        raise
                    else:
                        msg = 'Qualitative trait "{}" has no {} value in translator\n'
                        sys.stderr.write(msg.format(trait_name, value))
                        continue

            try:
                obs = add_observation(obs_entity, trait_name, assayname,
                                      value, creation_time, observer)
                assign_perm('view_observation', perm_gr, obs)
            except ValueError as error:
                if raise_on_error:
                    raise
                else:
                    sys.stderr.write(str(error) + '\n')
                    continue


NOT_USED_OBSERVATION_FILE_FIELDS = ('remarks', COLNUMBER_HEADER, 'Remarks',
                                    'Mean_petal_length', 'Mean_petal_width',
                                    'Mean_sepal_length', 'mean_sepal_width',
                                    'Average_Fruit_weight_g', 'Leaf angle 1',
                                    'Leaf angle 2')


def _delete_unused_fields(entry):
    for field in NOT_USED_OBSERVATION_FILE_FIELDS:
        try:
            del entry[field]
        except KeyError:
            pass


def _parse_trait_values(entry, qualitative_transcriptors=None):
    trait_value = {}
    morpho_points, morpho_values = _process_morpho_points(entry)
    if morpho_values:
        trait_value[morpho_points] = morpho_values
    for key, value in _process_color_data(entry):
        trait_value[key] = value
    for key, value in entry.items():
        # process and change any particular trait
        if qualitative_transcriptors and key in qualitative_transcriptors:
            value = qualitative_transcriptors[value]

        trait_value[key] = value
    return trait_value


def _process_color_data(entry):
    l_minolta = entry.pop('External fruit color L', None)
    b_minolta = entry.pop('External fruit color b', None)
    a_minolta = entry.pop('External fruit color a', None)
    if l_minolta and b_minolta and a_minolta:
        lba = json.dumps({'L': l_minolta, 'B': b_minolta, 'A': a_minolta})
        yield 'External fruit color LAB', lba

    red_average = entry.pop('Average Red', None)
    green_average = entry.pop('Average Green', None)
    blue_average = entry.pop('Average Blue', None)
    lum_average = entry.pop('Average Luminosity', None)
    if red_average and green_average and blue_average:
        rgb = json.dumps({'R': red_average, 'G': green_average,
                          'B': blue_average, 'lum': lum_average})
        yield 'Average RGB', rgb

    l_average = entry.pop('Average L Value', None)
    a_average = entry.pop('Average a Value', None)
    b_average = entry.pop('Average b Value', None)
    hue_average = entry.pop('Average Hue', None)
    chroma_average = entry.pop('Average Chroma', None)
    if l_average and a_average and b_average and hue_average and chroma_average:
        average_lba = json.dumps({'L': l_average, 'B': b_average,
                                  'A': a_average, 'chroma': chroma_average,
                                  'hue': hue_average})
        yield 'Average LAB', average_lba

    for num in range(1, 5):
        l_part = entry.pop('L{}'.format(num), None)
        a_part = entry.pop('a{}'.format(num), None)
        b_part = entry.pop('b{}'.format(num), None)
        if l_part and a_part and b_part:
            lab_color = json.dumps({'L': l_part, 'A': a_part, 'B': b_part})
            yield 'LAB Color{}'.format(num), lab_color

    l_average = entry.pop('mean_L', None)
    a_average = entry.pop('mean_a', None)
    b_average = entry.pop('mean_b', None)
#     hue_average = entry.pop('Average Hue', None)
#     chroma_average = entry.pop('Average Chroma', None)
    if l_average and a_average and b_average and hue_average and chroma_average:
        average_lba = json.dumps({'L': l_average, 'B': b_average,
                                  'A': a_average, 'chroma': chroma_average,
                                  'hue': hue_average})
        yield 'Average LAB Color', average_lba


def _process_morpho_points(entry):
    morpho_points = []
    for num in range(1, 11):
        x_point = '{}x'.format(num)
        y_point = '{}y'.format(num)
        x_point_val = entry.pop(x_point, None)
        y_point_val = entry.pop(y_point, None)
        if x_point_val is None or y_point_val is None:
            continue
        morpho_points.append({x_point: x_point_val,
                              y_point: y_point_val})
    if morpho_points:
        morpho_points = json.dumps(morpho_points)
    return ('Morphometric points', morpho_points)


def add_excel_related_observations(fpath, assay_header=ASSAY_HEADER,
                                   plant_header=PLANT_HEADER,
                                   plant_part_header=PLANT_PART_HEADER,
                                   accession_header=ACCESSION_HEADER,
                                   photo_header=PHOTO_HEADER,
                                   perm_gr=None,
                                   one_part_per_plant=False,
                                   qual_translator=None):

    rel_type = Cvterm.objects.get(cv__name='relationship_types',
                                  name='obtained_from')
    with transaction.atomic():
        for entry in excel_dict_reader(fpath):
            plant_name = entry.pop(plant_header)
            accession_number = entry.pop(accession_header)
            plant_part = entry.pop(plant_part_header)
            assay_name = entry.pop(assay_header)

            if perm_gr is None:
                perm_gr = assay_name
            perm_gr = Group.objects.get(name=perm_gr)

            try:
                photo_id = entry.pop(photo_header)
            except KeyError:
                photo_id = None
            try:
                observer = entry.pop('author')
            except KeyError:
                observer = None

            try:
                creation_time = entry.pop('date')
            except KeyError:
                creation_time = None

            _delete_unused_fields(entry)

            obs_image = None
            photo_uuid = None
            if photo_id:
                try:
                    obs_image = ObservationImages.objects.get(image__icontains=photo_id)
                    photo_uuid = obs_image.observation_image_uid
                except ObservationImages.DoesNotExist:
                    print(plant_name, plant_part, accession_number, photo_id)

            # create observation_entity
            obs_entity = get_or_create_obs_entity(accession_number, assay_name,
                                                  plant_part,
                                                  plant_name=plant_name,
                                                  perm_gr=perm_gr,
                                                  photo_uuid=photo_uuid,
                                                  one_part_per_plant=one_part_per_plant)
            # print(obs_entity)
            observation_pairs = _parse_trait_values(entry)
            # print(entry)
            # print(observation_pairs)
            for trait_name, value in observation_pairs.items():
                if not value:
                    continue
                if qual_translator and trait_name in qual_translator:
                    try:
                        value = qual_translator[trait_name][str(value)]
                    except KeyError:
                        raise KeyError('{} not in {} trait'.format(value, trait_name))

                observation = add_observation(obs_entity=obs_entity,
                                              trait_name=trait_name,
                                              assay_name=assay_name, value=value,
                                              creation_time=creation_time,
                                              observer=observer)

                if obs_image:
                    ObservationRelationship.objects.create(subject=observation,
                                                           object=obs_image.observation,
                                                           type=rel_type)
