import csv
import datetime
import os
from random import Random
import sys

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
                            ObservationEntityPlant)


TRAIT_PROPS_CV = 'trait_props'
TRAIT_TYPES_CV = 'trait_types'


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
            assay, created = Assay.objects.get_or_create(**assay_data)

            if created:
                for key, value in props.items():
                    type_ = Cvterm.objects.get(cv__name='assay_props',
                                               name=key)
                    AssayProp.objects.create(assay=assay, type=type_,
                                             value=value)
                group, created = Group.objects.get_or_create(name=assay.name)
                assign_perm('view_assay', group, assay)
                group.user_set.add(owner)


def add_or_load_observation(obs_entity, trait_name, assay_name, value,
                            creation_time, observer=None):
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
    try:
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
            name = row['name']
            type_ = row['type']
            description = row['description']
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

            if trait_created and description:
                desc_type = Cvterm.objects.get(cv__name=TRAIT_PROPS_CV,
                                               name='description')
                TraitProp.objects.create(trait=trait, type=desc_type,
                                         value=description)


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
                accession = Accession.objects.get(accession_number=accession_code)

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
                             plant_number=None, perm_gr=None):
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

    elif plant_name:
        obs_entity_name = suggest_obs_entity_name(plant_name, plant_part)
        obs_ent, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                   part=plant_part_type)
        if created:
            assign_perm('view_obs_entity', perm_gr, obs_ent)
            plant, p_creat = Plant.objects.get_or_create(plant_name=plant_name,
                                                         accession=accession)
            if p_creat:
                assign_perm('view_plant', perm_gr, plant)
                ObservationEntityPlant.objects.create(obs_entity=obs_ent,
                                                      plant=plant)
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
            if p_creat:
                assign_perm('view_plant', perm_gr, plant)
                ObservationEntityPlant.objects.create(obs_entity=obs_ent,
                                                      plant=plant)
                AssayPlant.objects.create(plant=plant, assay=assay)
    else:
        # hay que crear una obs entity con todas las plantas de este accession
        # en este ensayo

        obs_entity_name = '{}_{}_{}'.format(accession.accession_number,
                                            assay.name, plant_part)
        obs_ent, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                   part=plant_part_type)
        if created:
            plants = Plant.objects.filter(accession=accession,
                                          assayplant__assay=assay)
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


def add_or_load_excel_observations(fpath, observer=None, assay=None,
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
                    value = qualitative_translator[trait_name][value]
                except KeyError as error:
                    if raise_on_error:
                        raise
                else:
                    sys.stderr.write(str(error) + '\n')
                    continue

            try:
                obs = add_or_load_observation(obs_entity, trait_name, assayname,
                                              value, creation_time, observer)
                assign_perm('view_observation', perm_gr, obs)
            except ValueError as error:
                if raise_on_error:
                    raise
                else:
                    sys.stderr.write(str(error) + '\n')
                    continue
