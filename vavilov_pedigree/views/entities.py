from django.views.generic.detail import DetailView

from vavilov_pedigree.models import Accession, Assay, Plant, SeedLot
from vavilov_pedigree.views.tables import seedlot_to_table, plant_to_table
from django.views.generic.edit import DeleteView, UpdateView, CreateView


class AccessionDetail(DetailView):
    model = Accession
    slug_url_kwarg = 'accession_number'
    slug_field = 'accession_number'

    def get_context_data(self, **kwargs):
        context = super(AccessionDetail, self).get_context_data(**kwargs)
        context['accession'] = self.object
        context['seedlots'] = seedlot_to_table(self.object.seed_lots,
                                               self.request)
        return context


class AssayDetail(DetailView):
    model = Assay
    slug_url_kwarg = 'name'
    slug_field = 'name'

    def get_context_data(self, **kwargs):
        context = super(AssayDetail, self).get_context_data(**kwargs)
        context['assay'] = self.object
        return context


class PlantDetail(DetailView):
    model = Plant
    slug_url_kwarg = 'plant_name'
    slug_field = 'plant_name'

    def get_context_data(self, **kwargs):
        context = super(PlantDetail, self).get_context_data(**kwargs)
        context['plant'] = self.object
        context['clones'] = plant_to_table(self.object.clones, self.request)
        return context


class SeedLotDetail(DetailView):
    model = SeedLot
    slug_url_kwarg = 'name'
    slug_field = 'name'

    def get_context_data(self, **kwargs):
        context = super(SeedLotDetail, self).get_context_data(**kwargs)
        context['seedlot'] = self.object
        return context


def search_cross(request):
    pass

def search_seedlot(request):
    pass
