import csv
import sqlite3

from django.conf import settings as site_settings
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from guardian.shortcuts import assign_perm
from pytz import timezone

from vavilov.conf import settings
from vavilov.db_management.phenotype import (add_or_load_observation,
                                             suggest_plant_part_uid)
from vavilov.models import (Assay, Cvterm, Trait, TraitProp, Plant,
                            AssayPlant, Accession, AssayTrait,
                            AccessionSynonym, Observation, PlantPart)


OUR_TIMEZONE = timezone(site_settings.TIME_ZONE)
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
            if created:
                for assay in assays:
                    AssayTrait.objects.create(assay=assay, trait=trait)
                group = Group.objects.get(name=assay.name)
                assign_perm('view_trait', group, trait)
                # We nedd fielbook trait type to generate fieldbook db with the
                # observations. This is the only data that we need from fieldbook
                # traits
                TraitProp.objects.create(trait=trait,
                                         type=FIELBOOK_TRAIT_TYPE,
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
            unique_id = entry['unique_id']
            accession_code = entry.get(accession_header, None)

            if accession_code in ('UNKNOWN', None, ''):
                accession_code = entry.get(synonym_headers[0], unique_id)

            exp_field = entry.get(experimental_field_header, None)
            row = entry.get(row_header, None)
            column = entry.get(column_header, None)
            pot_number = entry.get(pot_number_header, None)

            new_plant = False
            try:
                plant = Plant.objects.get(unique_id=unique_id)
            except Plant.DoesNotExist:
                new_plant = True
            if not new_plant:
                continue

            accession, created = Accession.objects.get_or_create(code=accession_code)
            if created:
                assign_perm('view_accession', group, accession)

            plant = Plant.objects.create(unique_id=unique_id,
                                         accession=accession,
                                         experimental_field=exp_field,
                                         row=row, column=column,
                                         pot_number=pot_number)
            assign_perm('view_plant', group, plant)
            AssayPlant.objects.create(plant=plant, assay=assay)

            # Accession can be created with other plant of other field
            if synonym_headers is None:
                synonym_headers = []

            for synonym_header in synonym_headers:
                synonym = entry.get(synonym_header, None)
                if synonym is not None:
                    AccessionSynonym.objects.get_or_create(accession=accession,
                                                           type=synonym_header,
                                                           code=entry[synonym_header])


def add_or_load_fielbook_observations(fpath, observer, assays, excluded_traits=None,
                                      plant_part='plant'):
    fhand = open(fpath)
    if excluded_traits is None:
        excluded_traits = getattr(settings,
                                  'EXCLUDED_FIELDBOOK_TRAITS_TO_LOAD_IN_DB', [])

    conn = sqlite3.connect(fhand.name)
    cursor = conn.cursor()

    with transaction.atomic():
        for entry in cursor.execute("select * from user_traits"):
            plant = entry[1]
            trait = entry[2]
            if trait in excluded_traits:
                continue
            value = entry[4]
            creation_time = parse_datetime(entry[5])
            if len(entry) > 6:
                if entry[6] != ' ':
                    observer = entry[6]
            plant_part_uid = suggest_plant_part_uid(plant, plant_part)

            plant = Plant.objects.get(unique_id=plant)
            plant_part_cv = Cvterm.objects.get(cv__name='plant_parts',
                                               name=plant_part)
            plant_part_obj = PlantPart.objects.get_or_create(plant_part_uid=plant_part_uid,
                                                             plant=plant,
                                                             part=plant_part_cv)[0]
            add_or_load_observation(plant_part_obj, trait, assays, value,
                                    creation_time, observer)


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

# RAW_QUERY = "SELECT * FROM observation AS o "
# RAW_QUERY += "WHERE (o.creation_time = (SELECT MAX(creation_time) "
# RAW_QUERY += "FROM observation AS o2 WHERE o.project_id=o2.project_id "
# RAW_QUERY += "AND o.rid=o2.rid AND o.trait_id=o2.trait_id)) AND "
# RAW_QUERY += "(o.project_id IN (SELECT o3.project_id FROM project AS o3 "
# RAW_QUERY += "WHERE o3.project_set_id={}))"

# RAW_QUERY = "SELECT * FROM observation AS o "
# RAW_QUERY += "INNER JOIN plot "
# RAW_QUERY += "WHERE (o.creation_time = (SELECT MAX(creation_time) FROM observation AS o2 WHERE o.plot_id=o2.plot_id AND o.trait_id=o2.trait_id)) "
# RAW_QUERY += "AND (o.plot_id == plot.plot_id AND plot.project_id IN (SELECT p.project_id FROM project AS p WHERE p.project_set_id={}))"

SQLITE3_QUERY = '''
SELECT * FROM observation AS o
INNER JOIN plant_part
WHERE o.plant_part_id=plant_part.plant_part_id and plant_part.plant_part_id IN {} AND (o.creation_time = (SELECT MAX(creation_time)
                                               FROM observation AS o2
                                               WHERE o.plant_part_id=o2.plant_part_id AND o.trait_id=o2.trait_id))'''
POSTGRES_QUERY = '''
SELECT * FROM observation AS o
INNER JOIN plant_part
ON o.plant_part_id=plant_part.plant_part_id and plant_part.plant_part_id IN {} AND (o.creation_time = (SELECT MAX(creation_time)
                                               FROM observation AS o2
                                               WHERE o.plant_part_id=o2.plant_part_id AND o.trait_id=o2.trait_id))'''


def _to_fieldbook_local_time(utf_datetime):
    local_datetimetime = OUR_TIMEZONE.normalize(utf_datetime.astimezone(OUR_TIMEZONE))
    return local_datetimetime.strftime('%Y-%m-%d %H:%M:%S%z')


def _encode_plant_id_for_sql(plants):
    plantquery = Plant.objects.filter(unique_id__in=plants).values('plant_id')
    plant_ids = [plant['plant_id'] for plant in plantquery]
    if len(plant_ids) == 1:
        sqlized_plant_ids = '({})'.format(plant_ids[0])
    else:
        sqlized_plant_ids = str(tuple(plant_ids))
    return sqlized_plant_ids


def _encode_plant_part_id_for_sql(plants, plant_part):
    query = Q(plant__unique_id__in=plants) & Q(part__name=plant_part)
    plantpartquery = PlantPart.objects.filter(query).values('plant_part_id')
    plant_part_ids = [plant_part['plant_part_id'] for plant_part in plantpartquery]
    if len(plant_part_ids) == 1:
        sqlized_plant_part_ids = '({})'.format(plant_part_ids[0])
    else:
        sqlized_plant_part_ids = str(tuple(plant_part_ids))
    return sqlized_plant_part_ids


def insert_newest_observations(fhand, plants, excluded_traits=None,
                               plant_part='plant'):
    _create_empty_fieldbook_db(fhand)
    engine = _get_db_engine()
    con = sqlite3.connect(fhand.name)
    cur = con.cursor()
    query = Observation.objects

    if engine == 'sqlite3':
        query = query.raw(SQLITE3_QUERY.format(_encode_plant_part_id_for_sql(plants, plant_part)))
    elif engine == 'postgresql_psycopg2':
        query = query.raw(POSTGRES_QUERY.format(_encode_plant_part_id_for_sql(plants, plant_part)))
    else:
        raise NotImplementedError('This raw query is not implemented yet using this engine')

    for index, observation in enumerate(query):
        if excluded_traits and observation.trait.name in excluded_traits:
            continue
        local_creation_time = _to_fieldbook_local_time(observation.creation_time)
        fieldbook_trait_type = TraitProp.objects.get(trait=observation.trait,
                                                     type=FIELBOOK_TRAIT_TYPE)
        cur.execute('insert into user_traits (id, rid, parent, trait, userValue, timeTaken, person, location, rep, notes, exp_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (index + 1, observation.plant.unique_id, observation.trait.name, fieldbook_trait_type.value, observation.value,
                     local_creation_time, observation.observer, '', '1', '', ''))
    cur.close()
    con.commit()
