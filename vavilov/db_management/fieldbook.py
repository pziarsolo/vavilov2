import csv
import sqlite3

from django.conf import settings as site_settings
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from guardian.shortcuts import assign_perm

from vavilov.conf import settings
from vavilov.conf.settings import OUR_TIMEZONE
from vavilov.db_management.phenotype import (add_or_load_observation,
                                             suggest_obs_entity_name)
from vavilov.models import (Assay, Cvterm, Trait, TraitProp, Plant,
                            AssayPlant, Accession, AssayTrait,
                            Observation, ObservationEntity,
                            ObservationEntityPlant)


FIELDBOOK_TO_DB_TYPE_TRANSLATOR = {'categorical': 'text', 'numeric': 'numeric',
                                   'percent': 'percent', 'date': 'date',
                                   'text': 'text', 'boolean': 'boolean',
                                   'counter': 'numeric', 'rust rating': 'text'}
TRAIT_TYPES_CV = 'trait_types'
FIELBOOK_TRAIT_TYPE = 'fieldbook_trait_type'


class trt_dialect(csv.excel):
    delimiter = ','
    skipinitialspace = True
    doublequote = False
    lineterminator = '\n'


def add_or_load_fieldbook_traits(fpath, assays):
    excluded_traits = getattr(settings, 'EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB', [])
    with transaction.atomic():
        assays = Assay.objects.filter(name__in=assays)
        for entry in csv.DictReader(open(fpath), dialect=trt_dialect):
            name = entry['trait']
            type_ = entry['format']
            if name in excluded_traits:
                continue
            data_type = FIELDBOOK_TO_DB_TYPE_TRANSLATOR[type_]
            trait_type = Cvterm.objects.get(cv__name=TRAIT_TYPES_CV,
                                            name=data_type)
            trait, created = Trait.objects.get_or_create(name=name,
                                                         type=trait_type)
            for assay in assays:
                AssayTrait.objects.get_or_create(assay=assay, trait=trait)

            if created:
                for assay in assays:
                    group = Group.objects.get(name=assay.name)
                    assign_perm('view_trait', group, trait)
                # We nedd fielbook trait type to generate fieldbook db with the
                # observations. This is the only data that we need from fieldbook
                # traits
                trait_prop_trait = Cvterm.objects.get(name=FIELBOOK_TRAIT_TYPE)
                TraitProp.objects.create(trait=trait,
                                         type=trait_prop_trait,
                                         value=type_)


def add_or_load_fieldbook_fields(fpath, assay, accession_header,
                                 synonym_headers=None,
                                 experimental_field_header=None,
                                 row_header=None, column_header=None,
                                 pot_number_header=None):
    fhand = open(fpath)
    assay = Assay.objects.get(name=assay)
    group = Group.objects.get(name=assay.name)
    with transaction.atomic():
        for entry in csv.DictReader(fhand, dialect=trt_dialect):
            plant_name = entry['unique_id']
            accession_code = entry.get(accession_header, None)
            if accession_code in (None, 'UNKNOWN', ''):
                accession_code = entry.get(synonym_headers[0], None)
            exp_field = entry.get(experimental_field_header, None)
            row = entry.get(row_header, None)
            column = entry.get(column_header, None)
            pot_number = entry.get(pot_number_header, None)

            new_plant = False
            try:
                plant = Plant.objects.get(plant_name=plant_name)
            except Plant.DoesNotExist:
                new_plant = True
            if not new_plant:
                continue
            try:
                accession = Accession.objects.get(accession_number=accession_code)
            except Accession.DoesNotExist:
                print(accession_code, entry)
                raise

            plant = Plant.objects.create(plant_name=plant_name,
                                         accession=accession,
                                         experimental_field=exp_field,
                                         row=row, column=column,
                                         pot_number=pot_number)
            assign_perm('view_plant', group, plant)
            AssayPlant.objects.create(plant=plant, assay=assay)


def add_or_load_fielbook_observations(fpath, observer, assays, excluded_traits=None,
                                      plant_part='plant'):
    fhand = open(fpath)
    if excluded_traits is None:
        excluded_traits = getattr(settings,
                                  'EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB', [])

    conn = sqlite3.connect(fhand.name)
    cursor = conn.cursor()
    group = Group.objects.get(name=assays[0])

    with transaction.atomic():
        for entry in cursor.execute("select * from user_traits"):
            if len(entry) > 6:
                if entry[6] != ' ':
                    observer = entry[6]
            fieldbook_entry = {'rid': entry[1], 'parent': entry[2],
                               'userValue': entry[4], 'timeTaken': entry[5],
                               'person': observer}
            add_fieldbook_observations(fieldbook_entry, plant_part=plant_part,
                                       group=group, assay=assays[0],
                                       excluded_traits=excluded_traits)


def add_fieldbook_observations(entry, plant_part, assay, group=None,
                               excluded_traits=None):

    plant_name = entry['rid']
    trait = entry['parent']
    if excluded_traits and trait in excluded_traits:
        return
    value = entry['userValue']
    creation_time = parse_datetime(entry['timeTaken'])
    observer = entry['person']
    obs_entity_name = suggest_obs_entity_name(plant_name, plant_part)

    plant = Plant.objects.get(plant_name=plant_name)
    plant_part_cv = Cvterm.objects.get(cv__name='plant_parts',
                                       name=plant_part)
    obs_entity, created = ObservationEntity.objects.get_or_create(name=obs_entity_name,
                                                                  part=plant_part_cv)

    Assay.objects.get(name=assay)
    if group is None:
        group = Group.objects.get(name=assay)
    if created:
        ObservationEntityPlant.objects.create(obs_entity=obs_entity,
                                              plant=plant)
        assign_perm('view_obs_entity', group, obs_entity)

    observation, created = add_or_load_observation(obs_entity, trait, assay,
                                                   value, creation_time,
                                                   observer)

    assign_perm('view_observation', group, observation)
    return observation, created


# export db
def _create_empty_fieldbook_db(fhand):
    con = sqlite3.connect(fhand.name)
    cur = con.cursor()
    cur.execute("PRAGMA user_version = 6")
    cur.execute("CREATE TABLE android_metadata (locale TEXT)")
    cur.execute("INSERT INTO android_metadata values('en')")
    cur.execute("CREATE TABLE traits(id INTEGER PRIMARY KEY, trait TEXT, format TEXT, defaultValue TEXT, minimum TEXT, maximum TEXT, details TEXT, categories TEXT, isVisible TEXT, realPosition int)")
    cur.execute("CREATE TABLE user_traits(id INTEGER PRIMARY KEY, rid TEXT, parent TEXT, trait TEXT, userValue TEXT, timeTaken TEXT, person TEXT, location TEXT, rep TEXT, notes TEXT, exp_id TEXT)")
    cur.execute("CREATE TABLE range(id INTEGER PRIMARY KEY,`unique_id` TEXT,`Accesion` TEXT,`Inv` TEXT,`Fila_F` TEXT,`Maceta_M` TEXT,`Num_replica` TEXT,`BGV` TEXT)")
    cur.close()
    con.commit()


def _get_db_engine():
    return site_settings.DATABASES['default']['ENGINE'].split('.')[-1]


SQLITE3_QUERY = '''
SELECT * FROM vavilov_observation AS o
INNER JOIN vavilov_observation_entity AS oe
WHERE o.obs_entity_id=oe.obs_entity_id and oe.obs_entity_id IN {}
    AND (o.creation_time = (SELECT MAX(creation_time)
                            FROM vavilov_observation AS o2
                            WHERE o.obs_entity_id=o2.obs_entity_id AND o.trait_id=o2.trait_id))'''

POSTGRES_QUERY = '''
SELECT * FROM vavilov_observation AS o
INNER JOIN vavilov_observation_entity AS oe
ON o.obs_entity_id=oe.obs_entity_id and oe.obs_entity_id IN {}
    AND (o.creation_time = (SELECT MAX(creation_time)
                            FROM vavilov_observation AS o2
                            WHERE o.obs_entity_id=o2.obs_entity_id AND o.trait_id=o2.trait_id))'''


def to_fieldbook_local_time(utf_datetime):
    local_datetimetime = OUR_TIMEZONE.normalize(utf_datetime.astimezone(OUR_TIMEZONE))
    return local_datetimetime.strftime('%Y-%m-%d %H:%M:%S%z')


# def _encode_plant_id_for_sql(plants):
#     plantquery = Plant.objects.filter(unique_id__in=plants).values('plant_id')
#     plant_ids = [plant['plant_id'] for plant in plantquery]
#     if len(plant_ids) == 1:
#         sqlized_plant_ids = '({})'.format(plant_ids[0])
#     else:
#         sqlized_plant_ids = str(tuple(plant_ids))
#     return sqlized_plant_ids


def _encode_obs_entity_id_for_sql(plants, plant_part):
    query = Q(observationentityplant__plant__plant_name__in=plants) & Q(part__name=plant_part)
    plantpartquery = ObservationEntity.objects.filter(query).values('obs_entity_id')
    obs_entity_ids = [plant_part['obs_entity_id'] for plant_part in plantpartquery]
    if len(obs_entity_ids) == 1:
        sqlized_obs_entity_ids = '({})'.format(obs_entity_ids[0])
    else:
        sqlized_obs_entity_ids = str(tuple(obs_entity_ids))
    return sqlized_obs_entity_ids


def insert_newest_observations(fhand, plants, excluded_traits=None,
                               plant_part='plant'):
    _create_empty_fieldbook_db(fhand)
    engine = _get_db_engine()
    con = sqlite3.connect(fhand.name)
    cur = con.cursor()
    query = Observation.objects

    if engine == 'sqlite3':
        query = query.raw(SQLITE3_QUERY.format(_encode_obs_entity_id_for_sql(plants, plant_part)))
    elif engine == 'postgresql_psycopg2':
        query = query.raw(POSTGRES_QUERY.format(_encode_obs_entity_id_for_sql(plants, plant_part)))
    else:
        raise NotImplementedError('This raw query is not implemented yet using this engine')

    for index, observation in enumerate(query):
        if excluded_traits and observation.trait.name in excluded_traits:
            continue
        local_creation_time = to_fieldbook_local_time(observation.creation_time)
        fieldbook_trait_type = TraitProp.objects.get(trait=observation.trait,
                                                     type__name=FIELBOOK_TRAIT_TYPE)
        plant_name = observation.plants[0].plant_name
        cur.execute('insert into user_traits (id, rid, parent, trait, userValue, timeTaken, person, location, rep, notes, exp_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (index + 1, plant_name, observation.trait.name, fieldbook_trait_type.value, observation.value,
                     local_creation_time, observation.observer, '', '1', '', ''))
    cur.close()
    con.commit()
