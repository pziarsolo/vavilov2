import json
import re

from django.http.response import HttpResponse

from vavilov.caches import get_taxons
from vavilov.models import (Accession, AccessionSynonym, Plant, Trait,
                            Observation)


def accession_numbers(request):
    query = Accession.objects.all()
    query2 = AccessionSynonym.objects.filter(type__cv__name='synonym_types',
                                             type__name='collecting')
    if request.method == 'GET':
        if u'term' in request.GET:
            term = request.GET['term']
            query = query.filter(accession_number__icontains=term)
            query2 = query2.filter(synonym_code__icontains=term)
        if u'limit' in request.GET:
            try:
                limit = int(request.GET[u'limit'])
                query = query[:limit]
                query2 = query2[:limit]
            except ValueError:
                pass
    acc_numbers = set()
    for value in query.values('accession_number'):
        if 'accession_number' in value and value['accession_number']:
            acc_numbers.add(value['accession_number'])
    for value in query2.values('synonym_code'):
        if 'synonym_code' in value and value['synonym_code']:
            acc_numbers.add(value['synonym_code'])

    return HttpResponse(json.dumps(list(acc_numbers)),
                        content_type='application/json')


def taxons(request):
    taxons_long = get_taxons()
    if request.method == 'GET':
        if u'term' in request.GET:
            term = request.GET['term']
            term = re.compile(term, flags=re.IGNORECASE)
            taxons_long = [tl for tl in taxons_long if re.search(term, tl['label'],)]
        if u'limit' in request.GET:
            try:
                limit = int(request.GET[u'limit'])
                taxons_long = taxons_long[:limit]
            except ValueError:
                pass

    return HttpResponse(json.dumps(taxons_long),
                        content_type='application/json')


def plants(request):
    query = Plant.objects.all()
    if request.method == 'GET':
        if u'term' in request.GET:
            term = request.GET['term']
            query = query.filter(plant_name__icontains=term)

        if u'limit' in request.GET:
            try:
                limit = int(request.GET[u'limit'])
                query = query[:limit]
            except ValueError:
                pass

    ids = set([row['plant_name'] for row in query.values('plant_name')])
    return HttpResponse(json.dumps(sorted(list(ids))),
                        content_type='application/json')


def traits(request):
    traits = Observation.objects.values('trait').distinct()
    query = Trait.objects.filter(trait_id__in=traits)

    if request.method == 'GET':
        if u'term' in request.GET:
            term = request.GET['term']
            query = query.filter(name__icontains=term)

        if u'limit' in request.GET:
            try:
                limit = int(request.GET[u'limit'])
                query = query[:limit]
            except ValueError:
                pass

    ids = set([row['name'] for row in query.values('name')])
    return HttpResponse(json.dumps(sorted(list(ids))),
                        content_type='application/json')
