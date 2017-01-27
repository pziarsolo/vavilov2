import csv
import datetime
from os.path import join, dirname
import re

from django.apps import apps
from django.contrib.auth.models import User, Group
from django.core.management import execute_from_command_line
from django.db import transaction
from django.db.models import Q
from guardian.compat import get_user_model
from guardian.shortcuts import assign_perm

import vavilov
from vavilov.api.permissions import add_view_permissions
from vavilov.conf.settings import PUBLIC_GROUP_NAME
from vavilov.latlon import lat_to_deg, lon_to_deg
from vavilov.models import (Accession, Country, Passport, Location, Cvterm,
                            Cv, Taxa, TaxaRelationship, Person, Db, Dbxref,
                            AccessionRelationship, AccessionTaxa,
                            AccessionSynonym)


INITIAL_DATA_DIR = join(dirname(vavilov.__file__), 'data')
SHARED_INITIAL_DATA_DIR = join(INITIAL_DATA_DIR, 'shared')


SHARED_INITIAL_DATA_TO_LOAD = [('cv', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cv.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_biological_status.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_collecting_source.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_person_types.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_accession_types.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_accession_relationship_types.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_synonym_types.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_taxonomic_ranks.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_taxa_relationships.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_assay_props.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_trait_types.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_trait_props.csv')),
                               ('cvterm', join(SHARED_INITIAL_DATA_DIR, 'vavilov_cvterm_plant_parts.csv')),
                               ('country', join(SHARED_INITIAL_DATA_DIR, 'vavilov_country.csv')),
                               ]

NO_REF_TABLES = ['cv', 'db', 'country']
LAT_LON_DEG_REGEX = re.compile('-?[0-9]{1,3}\.[0-9]{2,8}')
PUBLIC_GROUP = Group.objects.get_or_create(name=PUBLIC_GROUP_NAME)[0]


class comma_dialect(csv.excel):
    delimiter = ','
    skipinitialspace = True
    doublequote = True
    lineterminator = '\n'


def flush_vavilov_tables():
    # traditom_aap_config = TraditomAppConfig()
    for model in apps.get_app_config('vavilov').get_models():
        model.objects.all().delete()


def add_or_load_users(fpath):
    for entry in csv.DictReader(open(fpath), dialect=comma_dialect):
        username = entry['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            if username == 'admin':
                user = User.objects.create_superuser(username=username,
                                                     email=entry['email'],
                                                     password=entry['password'])
            else:
                user = User.objects.create_user(username=username,
                                                email=entry['email'],
                                                password=entry['password'])
        PUBLIC_GROUP.user_set.add(user)


def add_or_load_persons(fhand):
    with transaction.atomic():
        for entry in csv.DictReader(fhand, dialect=comma_dialect):
            cv = Cv.objects.get(name='person_types')
            type_ = Cvterm.objects.get(cv=cv, name=entry['type'])
            Person.objects.get_or_create(name=entry['name'],
                                         description=entry['description'],
                                         type=type_)


def _add_or_load_no_ref_table_data(fhand, model):
    with transaction.atomic():
        for line in csv.DictReader(fhand, dialect=comma_dialect):
            model.objects.get_or_create(**line)


def add_or_load_cvs(fpath):
    _add_or_load_no_ref_table_data(open(fpath), Cv)


def add_or_load_dbs(fpath):
    _add_or_load_no_ref_table_data(open(fpath), Db)


def add_or_load_cvterm(fpath):
    fhand = open(fpath)
    with transaction.atomic():
        for entry in csv.DictReader(fhand, dialect=comma_dialect):
            dbxref = entry['dbxref']
            try:
                cv = Cv.objects.get(name=entry['cv'])
            except Cv.DoesNotExist:
                msg = 'cv {} not in the database'.format(entry['cv'])
                raise RuntimeError(msg)

            Cvterm.objects.get_or_create(cv=cv, name=entry['name'],
                                         definition=entry['definition'])
            if dbxref:
                db_name, accession = dbxref.split(':')
                db = Db.objects.get(name=db_name)
                Dbxref.objects.get_or_create(db=db, accession=accession)


def load_initial_data_from_dict(spec_to_load):
    for table, fixture in spec_to_load:

        if table in NO_REF_TABLES:
            cmd = ["manage.py", "add_no_reference_table", fixture,
                   '-t', table]
        else:
            cmd = ["manage.py", "add_{}".format(table), fixture]
        execute_from_command_line(cmd)


def load_initial_data():
    flush_vavilov_tables()
    User = get_user_model()
    anon = User.get_anonymous()
    PUBLIC_GROUP.user_set.add(anon)
    add_view_permissions(anon)
    load_initial_data_from_dict(SHARED_INITIAL_DATA_TO_LOAD)


def add_accessions(fhand, silent=True):
    group = Group.objects.get(name=PUBLIC_GROUP_NAME)
    for accession_data in csv.DictReader(fhand, dialect=comma_dialect):
        accession_data = {key.strip(): value.strip() for key, value in accession_data.items()}

        with transaction.atomic():
            _add_main_accession(accession_data, silent, view_perm_group=group)


def _add_main_accession(accession_data, silent, view_perm_group):
    # Accession
    seed_holder_code = accession_data['Accession number']
    seed_holder_institute = accession_data['Istitute code']
    accession = add_accession(seed_holder_code, seed_holder_institute)

    assign_perm('view_accession', view_perm_group, accession)
    # taxonomy
    if accession_data['Subtaxa']:
        subtaxa_items = accession_data['Subtaxa'].split(':')
        subtaxa_type = subtaxa_items[0]
        subtaxa_name = subtaxa_items[1]
    else:
        subtaxa_type = None
        subtaxa_name = None

    taxon = add_taxonomies(accession_data['Genus'], accession_data['Species'],
                           subtaxa=subtaxa_name, subtaxa_type=subtaxa_type)
    if taxon is not None:
        AccessionTaxa.objects.create(accession=accession, taxa=taxon[0])

    # Donor Accession
    donor_code = accession_data['Donor accession number']
    donor_institute = accession_data['Donor Institute code']
    if donor_code and donor_institute:
        donor_accession = add_accession(donor_code, donor_institute)
        assign_perm('view_accession', view_perm_group, donor_accession)
        is_duplicated_from = Cvterm.objects.get(cv__name='accession_relationship_types',
                                                name='is_duplicated_from')

        AccessionRelationship.objects.create(subject=accession,
                                             object=donor_accession,
                                             type=is_duplicated_from)
    else:
        donor_accession = None

    # Duplicated accessions
    duplicated_code = accession_data['Code of duplicates in other genebank']
    duplicated_institute = accession_data['Code of the genebank holder of the duplicate']
    if duplicated_code and duplicated_institute:
        duplicated_acc = add_accession(duplicated_code, duplicated_institute)
        assign_perm('view_accession', view_perm_group, duplicated_acc)
        is_duplicated_from = Cvterm.objects.get(cv__name='accession_relationship_types',
                                                name='is_a_duplicated')
        AccessionRelationship.objects.create(subject=accession,
                                             object=duplicated_acc,
                                             type=is_duplicated_from)
    # collecting_accession is a synonym
    collecting_code = accession_data['Collecting number']
    collecting_institute = accession_data['Collecting institute code']
    if collecting_code and collecting_institute:
        collecting_inst = Person.objects.get(name=collecting_institute)
        collecting_type = Cvterm.objects.get(cv__name='synonym_types',
                                             name='collecting')

        AccessionSynonym.objects.create(accession=accession,
                                        synonym_institute=collecting_inst,
                                        synonym_code=collecting_code,
                                        type=collecting_type)
    # passport_data
    local_name = accession_data['Local name'] if accession_data['Local name'] else None
    traditional_location = accession_data['Traditional location'] if accession_data['Traditional location'] else None
    collecting_site = accession_data['Collecting site'] if accession_data['Collecting site'] else None
    collecting_province = accession_data['Province'] if accession_data['Province'] else None
    collecting_region = accession_data['Region'] if accession_data['Region'] else None
    collecting_country = accession_data['Country'] if accession_data['Country'] else None
    latitude = accession_data['Latitude'] if accession_data['Latitude'] else None
    longitude = accession_data['Longitude'] if accession_data['Longitude'] else None
    altitude = accession_data['Altitude'] if accession_data['Altitude'] else None
    biological_status = accession_data['Biological status of accession'] if accession_data['Biological status of accession'] else None
    collecting_source = accession_data['Collecting source'] if accession_data['Collecting source'] else None
    acquisition_date = accession_data['Acquisition date'] if accession_data['Acquisition date'] else None
    collecting_date = accession_data['Collecting date'] if accession_data['Collecting date'] else None

    add_passport_data(accession, local_name=local_name,
                      traditional_location=traditional_location,
                      site=collecting_site, province=collecting_province,
                      region=collecting_region, country=collecting_country,
                      latitude=latitude, longitude=longitude,
                      altitude=altitude, biological_status=biological_status,
                      collecting_source=collecting_source,
                      acquisition_date=acquisition_date,
                      collecting_date=collecting_date, silent=silent,
                      view_perm_group=view_perm_group)


def add_passport_data(accession, local_name=None, traditional_location=None,
                      site=None, province=None, region=None, country=None,
                      latitude=None, longitude=None, altitude=None,
                      biological_status=None, collecting_source=None,
                      acquisition_date=None, collecting_date=None,
                      silent=False, view_perm_group=None):

    if country is not None:
        try:
            country = Country.objects.get(Q(code2=country) | Q(code3=country) |
                                          Q(name=country))
        except Country.DoesNotExist:
            msg = 'Could not find country code {}: {}'
            print(msg.format(accession.accession_number, country))
            country = None

    if biological_status is not None:
        biological_status = Cvterm.objects.get(cv__name='biological_status',
                                               name=biological_status)
    if collecting_source is not None:
        collecting_source = Cvterm.objects.get(cv__name='collecting_source',

                                               name=collecting_source)

    if latitude is not None:
        if 'N' in latitude or 'S' in latitude:
            try:
                latitude = lat_to_deg(latitude)
            except ValueError:
                if not silent:
                    msg = 'Could not convert Latitude data {}: {}'
                    print(msg.format(accession.accession_number, latitude))
                latitude = None
        elif LAT_LON_DEG_REGEX.match(latitude):
            latitude = float(latitude)
        else:
            if not silent:
                    msg = 'Could not convert Latitude data {}: {}'
                    print(msg.format(accession.accession_number, latitude))
            latitude = None

    if longitude is not None:
        if 'E' in longitude or 'W' in longitude:
            try:
                longitude = lon_to_deg(longitude)
            except ValueError:
                if not silent:
                    msg = 'Could not convert Longitude data {}: {}'
                    print(msg.format(accession.accession_number, longitude))
                longitude = None

        elif LAT_LON_DEG_REGEX.match(longitude):
            longitude = float(longitude)
        else:
            if not silent:
                msg = 'Could not convert Longitude data {}: {}'
                print(msg.format(accession.accession_number, longitude))
            longitude = None
    if altitude is not None:
        altitude = str(altitude).replace('m', '').strip()

    if acquisition_date is not None:
        try:
            acquisition_date = _strtime_to_date(acquisition_date)
        except ValueError:
            if not silent:
                msg = 'bad acquisition time field {}: {}'
                print(msg.format(accession.accession_number, acquisition_date))
            acquisition_date = None

    if collecting_date is not None:
        try:
            collecting_date = _strtime_to_date(collecting_date)
        except ValueError:
            if not silent:
                msg = 'bad collecting_date time field {}: {}'
                print(msg.format(accession.accession_number, collecting_date))
            collecting_date = None

    location = add_location(site=site, province=province,
                            country=country, region=region, altitude=altitude,
                            longitude=longitude, latitude=latitude)

    passport = Passport.objects.create(accession=accession,
                                       local_name=local_name,
                                       traditional_location=traditional_location,
                                       location=location,
                                       biological_status=biological_status,
                                       collecting_source=collecting_source,
                                       acquisition_date=acquisition_date,
                                       collecting_date=collecting_date)

    if view_perm_group:
        assign_perm('vavilov.view_location', view_perm_group, location)
        assign_perm('vavilov.view_passport', view_perm_group, passport)

    return passport


def add_location(site=None, province=None, region=None, longitude=None,
                 country=None, latitude=None, altitude=None):
    if site or province or region or longitude or (latitude and longitude) or altitude or country:
        location = Location.objects.get_or_create(site=site, province=province,
                                                  region=region,
                                                  country=country,
                                                  longitude=longitude,
                                                  latitude=latitude,
                                                  altitude=altitude)
        return location[0]
    else:
        return None


def add_taxonomies(genus, species=None, subtaxa=None, subtaxa_type=None):
    taxo_cv = Cv.objects.get(name='taxonomic_ranks')
    main_taxon = None
    if genus:
        genus = genus[0].upper() + genus[1:].lower()
        genus_cvterm = Cvterm.objects.get(cv=taxo_cv, name='Genus')
        genus_tx = Taxa.objects.get_or_create(name=genus, rank=genus_cvterm)[0]
        main_taxon = (genus_tx, None)

    if genus and species:
        species = species.split(' ', 1)[0].lower()
        species_tx = _add_taxa(species, 'Species', genus_tx)
        main_taxon = (species_tx, None)

    if genus and species and subtaxa and subtaxa_type:
        subtaxa_tx = _add_taxa(subtaxa, subtaxa_type, species_tx)
        main_taxon = (subtaxa_tx, None)

    return main_taxon


def _add_taxa(taxa_name, taxa_rank_name, parent_taxa):
    taxo_cv = Cv.objects.get(name='taxonomic_ranks')
    taxa_rank = Cvterm.objects.get_or_create(cv=taxo_cv, name=taxa_rank_name)[0]
    is_a = Cvterm.objects.get(cv__name='taxa_relationships', name='is_a')
    try:
        tr = TaxaRelationship.objects.get(taxa_subject__name=taxa_name,
                                          taxa_subject__rank=taxa_rank,
                                          taxa_object=parent_taxa,
                                          type=is_a)
        taxa_in_db = True
    except TaxaRelationship.DoesNotExist:
        taxa_in_db = False

    if not taxa_in_db:
        taxa = Taxa.objects.create(name=taxa_name, rank=taxa_rank)
        TaxaRelationship.objects.create(taxa_subject=taxa,
                                        taxa_object=parent_taxa,
                                        type=is_a)
    else:
        taxa = tr.taxa_subject
    return taxa


def add_accession(accession, institute_name, acc_type=None, make_link=True):
    dbxref = None

    if acc_type is not None:
        acc_type = Cvterm.objects.get(cv__name='accession_types',
                                      name=acc_type)

    institute = Person.objects.get(name=institute_name)
    accession = Accession.objects.get_or_create(accession_number=accession,
                                                institute=institute,
                                                type=acc_type,
                                                dbxref=dbxref)
    return accession[0]


def _strtime_to_date(str_date):
    str_date = str(str_date)
    try:
        year = int(str_date[:4])
    except ValueError:
        return None
    try:
        month = int(str_date[4:6])
    except (IndexError, ValueError):
        month = 1
    try:
        day = int(str_date[4:6])
    except (IndexError, ValueError):
        day = 1

    return datetime.date(year, month, day)
