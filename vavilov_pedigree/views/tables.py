import django_tables2 as tables
from django_tables2.utils import A
from django_tables2.config import RequestConfig


class PlantTable(tables.Table):
    plant = tables.LinkColumn('pedigree;plant-detail', args=[A('plant_name')],
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


def seedlot_to_table(seed_lots, request):
    if seed_lots:
        seedlot_table = SeedLotTable(seed_lots, template='table.html',
                                     prefix='seed_lot-')
        RequestConfig(request).configure(seedlot_table)
    else:
        seedlot_table = None
    return seedlot_table

def plant_to_table(plants, request):
    if plants:
        plant_table = PlantTable(plants, template='table.html',
                                     prefix='seed_lot-')
        RequestConfig(request).configure(plant_table)
    else:
        plant_table = None
    return plant_table
