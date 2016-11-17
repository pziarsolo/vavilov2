
from django.db.models import Q
import django_filters
from django_filters.filters import MethodFilter

from vavilov.conf.settings import GENEBANK_CODE
from vavilov.models import (Taxa, get_bottom_taxons, Accession, Cvterm, Cv,
                            Db, Country, Assay, Plant)


class AccessionFilter(django_filters.FilterSet):
    # Accesion filter must be the first in process
    accession = MethodFilter(action='accession_number_filter')
    collecting_source = django_filters.NumberFilter(name='passport__collecting_source')
    country = django_filters.NumberFilter(name='passport__location__country')
    region = django_filters.CharFilter(name='passport__location__region',
                                       lookup_expr='icontains')
    biological_status = django_filters.NumberFilter(name='passport__biological_status')
    taxa = MethodFilter(action='accession_by_taxa')

    class Meta:
        model = Accession

    def accession_number_filter(self, queryset, value):
        # this is just the logic to get related accessions to value
        queryset2 = queryset.filter(Q(accession_number__icontains=value) |
                                    Q(accessionsynonym__synonym_code__icontains=value))
        accessions = []
        for accession in queryset2:
            if accession.institute.name == GENEBANK_CODE:
                accessions.append(accession)
            else:
                equivalents = accession.duplicated_accessions_and_equivalents
                equivalents = [equi for equi in equivalents
                               if equi.institute.name == GENEBANK_CODE]
                accessions.extend(equivalents)
        # this is the real filtering of the query
        list_ids = [accession.accession_id for accession in accessions]
        return queryset.filter(pk__in=list_ids)

    def accession_by_taxa(self, queryset, value):
        taxa = Taxa.objects.get(taxa_id=int(value))
        bottom_taxas = get_bottom_taxons([taxa])
        queryset = queryset.filter(accessiontaxa__taxa__in=bottom_taxas)
        return queryset


class DbFilter(django_filters.FilterSet):
    name = django_filters.CharFilter()

    class Meta:
        model = Db


class CvtermFilter(django_filters.FilterSet):
    cv = django_filters.CharFilter(name='cv__name')

    class Meta:
        model = Cvterm


class CvFilter(django_filters.FilterSet):
    name = django_filters.CharFilter()

    class Meta:
        model = Cv


class CountryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Country


class AssayFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Assay


class PlantFilter(django_filters.FilterSet):
    plant_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Plant
