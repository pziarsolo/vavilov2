from time import time
from django_tables2.utils import A
import django_tables2 as tables
from django_tables2.config import RequestConfig

from vavilov.conf.settings import (ACCESSION_TABLE_FIELDS,
                                   OBSERVATION_TABLE_FIELDS)
from vavilov.views.generic import calc_duration

value_template = '''{% if record.obtained_from.image %}
{{record.value_beauty|striptags|safe}}(<a href='/media/{{record.obtained_from.image}}' onclick="window.open('/media/{{record.obtained_from.image}}', 'newwindow', 'width=800, height=600'); return false;">image_origen</a>)
{% else %}
{{record.value_beauty|striptags|safe}}
{% endif %}'''

value_template = value_template.replace('\n', '')


class ObservationsTable(tables.Table):
    if 'accession' in OBSERVATION_TABLE_FIELDS:
        Accession = tables.LinkColumn('accession-detail', args=[A('accession.accession_number')],
                                      accessor=A('accession.accession_number'),
                                      orderable=False, verbose_name='Accession')
    if 'obs_entity' in OBSERVATION_TABLE_FIELDS:
        Obs_entity = tables.LinkColumn('obs_entity-detail', args=[A('obs_entity.name')],
                                       accessor=A('obs_entity.name'),
                                       orderable=True,
                                       verbose_name='Observation entity')
    if 'plant_part' in OBSERVATION_TABLE_FIELDS:
        plant_part = tables.Column('Plant part', accessor=A('obs_entity.part.name'),
                                   default='', orderable=True)
    if 'assay' in OBSERVATION_TABLE_FIELDS:
        assay = tables.LinkColumn('assay-detail', args=[A('assay.name')],
                                  accessor=A('assay.name'),
                                  orderable=True, verbose_name='Assay')
    if 'trait' in OBSERVATION_TABLE_FIELDS:
        trait = tables.LinkColumn('trait-detail', args=[A('trait.trait_id')],
                                  accessor=A('trait.name'),
                                  orderable=True, verbose_name='Trait')
    if 'value' in OBSERVATION_TABLE_FIELDS:
        value = tables.TemplateColumn(value_template, accessor=A('value'),
                                      default='', orderable=True)
    if 'observer' in OBSERVATION_TABLE_FIELDS:
        observer = tables.Column('Observer', accessor=A('observer'),
                                 default='', orderable=True)
    if 'creation_time' in OBSERVATION_TABLE_FIELDS:
        creation_time = tables.Column('Creation Time',
                                      accessor=A('creation_time'),
                                      default='', orderable=True)

    class Meta:
        attrs = {"class": "searchresult"}


class AccessionsTable(tables.Table):
    search_fields = ACCESSION_TABLE_FIELDS
    if 'accession_number' in search_fields:
        accession_number = tables.LinkColumn('accession-detail',
                                             args=[A('accession_number')],
                                             verbose_name='Accession')

    if 'collecting_number' in search_fields:
        collecting_number = tables.Column('Collecting number',
                                          accessor=A('collecting_number'),
                                          default='', orderable=False)

    if 'holder_number' in search_fields:
        holder_accession = tables.Column('Holder accession',
                                         accessor=A('holder_accession'),
                                         default='', orderable=False)
    if 'organism' in search_fields:
        organism = tables.Column('Organism',
                                 accessor=A('organism'),
                                 default='', orderable=False)

    if 'country' in search_fields:
        country = tables.Column('Collecting country',
                                accessor=A('collecting_country.__str__'),
                                default='', orderable=False)

    if 'region' in search_fields:
        region = tables.Column('Collecting Region',
                               accessor=A('collecting_region'),
                               default='', orderable=False)

    if 'province' in search_fields:
        province = tables.Column('Collecting province',
                                 accessor=A('collecting_province'),
                                 default='', orderable=False)
    if 'local_name' in search_fields:
        local_name = tables.Column('Local Name',
                                   accessor=A('local_name'),
                                   default='', orderable=False)
    if 'collecting_date' in search_fields:
        collecting_date = tables.Column('Collecting date',
                                        accessor=A('collecting_date'),
                                        default='', orderable=False)

    class Meta:
        attrs = {"class": "searchresult"}


class PlantsTable(tables.Table):
    plant = tables.LinkColumn('plant-detail', args=[A('plant_name')],
                              accessor=A('plant_name'), orderable=True,
                              verbose_name='Plant')
    Accession = tables.LinkColumn('accession-detail', args=[A('accession.accession_number')],
                                  accessor=A('accession.accession_number'),
                                  orderable=True, verbose_name='Accession')
    Exp_field = tables.Column('Experimentalfield',
                              accessor=A('experimental_field'))
    row = tables.Column('Row', accessor=A('row'))
    column = tables.Column('Column', accessor=A('column'))
    pot_number = tables.Column('Pot number', accessor=A('pot_number'))

    class Meta:
        attrs = {"class": "searchresult"}


class AssaysTable(tables.Table):
    assay = tables.LinkColumn('assay-detail', args=[A('name')],
                              accessor=A('name'),
                              orderable=True, verbose_name='Assay')
    description = tables.Column('Description', accessor=A('description'))
    owner = tables.Column('Owner', accessor=A('owner.username'),
                          orderable=True)
    start_date = tables.Column('Start date', accessor=A('start_date'))
    end_date = tables.Column('End date', accessor=A('end_date'))
    location = tables.Column('Location', accessor=A('location'))
    campaign = tables.Column('Campaign', accessor=A('campaign'))

    class Meta:
        attrs = {"class": "searchresult"}


def obs_to_table(observations, request):
    prev_time = time()
    observations_table = ObservationsTable(observations, template='table.html',
                                           prefix='observations-')
    prev_time = calc_duration('Observation: table creation', prev_time)
    RequestConfig(request).configure(observations_table)
    prev_time = calc_duration('Observation_ RequestConfig.configure', prev_time)
    return observations_table


def plants_to_table(plants, request):
    prev_time = time()
    plant_table = PlantsTable(plants, template='table.html', prefix='plant-')
    prev_time = calc_duration('Plant: table creation', prev_time)
    RequestConfig(request).configure(plant_table)
    prev_time = calc_duration('Plant: RequestConfig.configure', prev_time)
    return plant_table


def assays_to_table(assays, request):
    prev_time = time()
    assay_table = AssaysTable(assays, template='table.html', prefix='assay-')
    prev_time = calc_duration('Assay: table creation', prev_time)
    RequestConfig(request).configure(assay_table)
    prev_time = calc_duration('Assay: RequestConfig.configure', prev_time)
    return assay_table
