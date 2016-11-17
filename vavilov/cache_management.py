import json

from vavilov.conf.settings import SEARCH_CHOICES_CACHE_FILE, TAXONS_CACHE_FILE
from vavilov.models import Passport, AccessionTaxa, get_top_taxons


def _get_passport_data_choices():
    countries = set()
    bio_statuses = set()
    col_sources = set()
    regions = set()
    for pas in Passport.objects.all():
        if pas.location and pas.location.country:
            countries.add(pas.location.country)
        if pas.location and pas.location.region:
            regions.add(pas.location.region)
        if pas.biological_status:
            bio_statuses.add(pas.biological_status)
        if pas.collecting_source:
            col_sources.add(pas.collecting_source)

    country_choices = [('', '')]
    for country in countries:
        country_choices.append((country.country_id, '{}({})'.format(country.name,
                                                                    country.code2)))
    bio_status_choices = [('', '')]
    for bio_stat in bio_statuses:
        bio_status_choices.append((bio_stat.cvterm_id, '{}({})'.format(bio_stat.name,
                                                                       bio_stat.definition)))

    col_sources_choices = [('', '')]
    for col_source in col_sources:
        col_sources_choices.append((col_source.cvterm_id, '{}({})'.format(col_source.name,
                                                                          col_source.definition)))
    region_choices = [('', '')]
    for region in regions:
        region_choices.append((region, region))

    return {'country': country_choices,
            'biological_status': bio_status_choices,
            'collecting_source': col_sources_choices,
            'region': region_choices}


def get_taxons():
    taxons_long = []
    for acc_taxa in AccessionTaxa.objects.all():
        taxa = acc_taxa.taxa
        taxons = get_top_taxons(taxa)[::-1]
        previous = None
        for taxon in taxons:
            name = taxon.name
            if previous is not None:
                name = previous + ' ' + name
            taxa_data = {'label': name, 'value': taxon.taxa_id}
            if taxa_data not in taxons_long:
                taxons_long.append(taxa_data)
            previous = name
    return taxons_long


def update_caches():
    fhand = open(SEARCH_CHOICES_CACHE_FILE, 'w')
    search_choices = _get_passport_data_choices()
    json.dump(search_choices, fhand)
    fhand.close()

    taxons = get_taxons()
    fhand = open(TAXONS_CACHE_FILE, 'w')
    json.dump(taxons, fhand)
    fhand.close()
