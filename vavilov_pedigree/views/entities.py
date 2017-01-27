from django.http.response import HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_tables2.config import RequestConfig

from django_tables2.utils import A
import django_tables2 as tables

from vavilov_pedigree.models import Accession, Assay, Plant, SeedLot


def accession(request, accession_number):
    context = RequestContext(request)
    try:
        acc = Accession.objects.get(accession_number=accession_number)
    except Accession.DoesNotExist:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    context['accession'] = acc
    # Seedlots
    seedlot_table = SeedLotTable(acc.seed_lots, template='table.html',
                                 prefix='seed_lot-')
    RequestConfig(request).configure(seedlot_table)
    context['seedlots'] = seedlot_table
    template = 'vavilov_pedigree/accession.html'
    return render_to_response(template, context)


def assay(request, name):
    context = RequestContext(request)
    try:
        assay = Assay.objects.get(name=name)
    except Assay.DoesNotExist:
        assay = None
    context['assay'] = assay

    template = 'vavilov_pedigree/assay.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)


class PlantsTable(tables.Table):
    plant = tables.LinkColumn('pedigree_plant_view', args=[A('plant_name')],
                              accessor=A('plant_name'), orderable=True,
                              verbose_name='Plant')
    Seedlot = tables.LinkColumn('pedigree_seedlot_view', args=[A('seed_lot.name')],
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
    Seedlot = tables.LinkColumn('pedigree_seedlot_view', args=[A('name')],
                                accessor=A('name'),
                                orderable=True, verbose_name='SeedLot')
    father = tables.LinkColumn('pedigree_plant_view', args=[A('father.plant_name')],
                               accessor=A('father.plant_name'), orderable=True,
                               verbose_name='Father')
    mother = tables.LinkColumn('pedigree_plant_view', args=[A('mother.plant_name')],
                               accessor=A('mother.plant_name'), orderable=True,
                               verbose_name='mother')

    class Meta:
        attrs = {"class": "searchresult"}


def plant(request, plant_name):
    context = RequestContext(request)
    try:
        plant = Plant.objects.get(plant_name=plant_name)
    except Plant.DoesNotExist:
        plant = None
    context['plant'] = plant

    # Clones
    clones_table = PlantsTable(plant.clones, template='table.html',
                               prefix='clones-')
    RequestConfig(request).configure(clones_table)
    context['clones'] = clones_table

    template = 'vavilov_pedigree/plant.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)


def seed_lot(request, name):
    context = RequestContext(request)
    try:
        seedlot = SeedLot.objects.get(name=name)
    except Plant.DoesNotExist:
        seedlot = None
    context['seedlot'] = seedlot

    template = 'vavilov_pedigree/seedlot.html'
    content_type = None
    return render_to_response(template, context, content_type=content_type)


def search_cross(request):
    pass

def search_seedlot(request):
    pass

