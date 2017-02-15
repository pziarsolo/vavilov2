import django_tables2 as tables
from django_tables2.utils import A
from django_tables2.config import RequestConfig


class AccessionTable(tables.Table):
    Accession_number = tables.LinkColumn('pedigree:accession-detail', args=[A('accession_number')],
                                         accessor=A('accession_number'), orderable=True,
                                         verbose_name='accession_number')

    Exp_field = tables.Column('Collecting number',
                              accessor=A('collecting_number'))
    Seedlots = tables.Column('Seed lots', accessor=A('seed_lots_beauty'))

    class Meta:
        attrs = {"class": "searchresult"}


class PlantTable(tables.Table):
    plant = tables.LinkColumn('pedigree:plant-detail', args=[A('plant_name')],
                              accessor=A('plant_name'), orderable=True,
                              verbose_name='Plant')
    Seedlot = tables.LinkColumn('pedigree:seedlot-detail', args=[A('seed_lot.name')],
                                accessor=A('seed_lot.name'),
                                orderable=True, verbose_name='SeedLot')
    Exp_field = tables.Column('Experimentalfield',
                              accessor=A('experimental_field'))
    row = tables.Column('Row', accessor=A('row'))
    column = tables.Column('Column', accessor=A('column'))
    pot_number = tables.Column('Pot number', accessor=A('pot_number'))

    class Meta:
        attrs = {"class": "searchresult"}


class SeedLotTable(tables.Table):
    Seedlot = tables.LinkColumn('pedigree:seedlot-detail', args=[A('name')],
                                accessor=A('name'),
                                orderable=True, verbose_name='SeedLot')
    father = tables.Column('Father', accessor=A('father'), orderable=True)
    mother = tables.Column('Mother', accessor=A('mother'), orderable=True)

    class Meta:
        attrs = {"class": "searchresult"}


def seedlot_to_table(seed_lots, request, obj_per_page=7):
    if seed_lots:
        seedlot_table = SeedLotTable(seed_lots, template='table.html',
                                     prefix='seed_lot-')
        RequestConfig(request, paginate={'per_page': obj_per_page}).configure(
            seedlot_table)
    else:
        seedlot_table = None
    return seedlot_table


def plant_to_table(plants, request, obj_per_page=7):
    if plants:
        plant_table = PlantTable(plants, template='table.html',
                                 prefix='plant-')
        RequestConfig(request, paginate={'per_page': obj_per_page}).configure(
            plant_table)
    else:
        plant_table = None
    return plant_table


def accession_to_table(accessions, request, obj_per_page=7):
    if accessions:
        accession_table = AccessionTable(accessions, template='table.html',
                                         prefix='accession-')
        RequestConfig(request, paginate={'per_page': obj_per_page}).configure(
            accession_table)
    else:
        accession_table = None
    return accession_table
