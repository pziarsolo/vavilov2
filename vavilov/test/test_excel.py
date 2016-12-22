import os
import tempfile

from django.contrib.auth.models import User, Group
from django.test import TestCase
from openpyxl import load_workbook

from vavilov.db_management.base import load_initial_data
from vavilov.db_management.excel import (write_excel_observations_skeleton,
                                               add_or_load_excel_observations,
                                               add_or_load_excel_traits)
from vavilov.db_management.fieldbook import (add_or_load_fieldbook_fields,
                                                   add_or_load_fieldbook_traits,
                                                   OUR_TIMEZONE)
from vavilov.models import Assay, Observation, Trait
from vavilov.tests.test_db_management import (TEST_DATA_DIR,
                                                    NSF1_PLANTS,
                                                    NSF1_LEAF_TRAITS,
                                                    EXCEL_TRAIT_FPATH)


FIELD_REDUCED_FPATH = os.path.join(TEST_DATA_DIR, 'NSF1_CN02_reduced_field.csv')
EXCEL_WITH_OBSERVATIONS_FPATH = os.path.join(TEST_DATA_DIR,
                                             'manualy_generated_data.xlsm')
NSF1_LEAF_TRAITS_EXCEL = '.'.join(NSF1_LEAF_TRAITS.split('.')[:-1]) + '.xlsx'


class ExcelLoadTests(TestCase):

    def setUp(self):
        load_initial_data()
        user = User.objects.create(username='user', email='t@t.es', password='pass')
        Assay.objects.create(name='assay1', owner=user)
        Group.objects.create(name='assay1')
        add_or_load_fieldbook_fields(NSF1_PLANTS, 'assay1',
                                     accession_header='BGV',
                                     synonym_headers=['Accession'])
        add_or_load_fieldbook_traits(NSF1_LEAF_TRAITS, assay='assay1')

    def test_add_excel_observations(self):
        assert len(Observation.objects.all()) == 0
        add_or_load_excel_observations(EXCEL_WITH_OBSERVATIONS_FPATH, 'test',
                                       'assay1', plant_part="plant")
        obs = Observation.objects.all()
        assert obs.count() == 3
        creation_time = obs[0].creation_time
        assert creation_time.tzname() == 'UTC'
        assert str(creation_time) == "2016-06-07 13:34:13+00:00"

        creation_time = OUR_TIMEZONE.normalize(creation_time.astimezone(OUR_TIMEZONE))
        assert creation_time.tzname() == 'CEST'
        assert str(creation_time) == "2016-06-07 15:34:13+02:00"

        add_or_load_excel_observations(EXCEL_WITH_OBSERVATIONS_FPATH, 'test',
                                       'assay1', plant_part="leaf")
        obs = Observation.objects.all()
        assert obs.count() == 6

    def test_add_excel_traits(self):
        add_or_load_excel_traits(EXCEL_TRAIT_FPATH, assay='assay1')
        assert Trait.objects.filter(type__name='image').count() == 2


class ExcelCreateTest(TestCase):

    def setUp(self):
        load_initial_data()
        user = User.objects.create(username='user', email='t@t.es',
                                   password='pass')
        Assay.objects.create(name='NSF1', owner=user)
        Group.objects.create(name='NSF1')
        add_or_load_fieldbook_fields(NSF1_PLANTS, 'NSF1',
                                     accession_header='BGV',
                                     synonym_headers=['Accession'])
        add_or_load_fieldbook_traits(NSF1_LEAF_TRAITS, assay='NSF1')

    def test_create_excel(self):
        # creates excel
        out_fhand = tempfile.NamedTemporaryFile(suffix='.xlsm')
        write_excel_observations_skeleton(FIELD_REDUCED_FPATH,
                                          NSF1_LEAF_TRAITS,
                                          out_fhand,
                                          accession_header='BGV',
                                          synonym_header='Accession',
                                          row_header='Fila_F',
                                          pot_number_header='Maceta_M',
                                          rows_per_plant=2)

        workbook = load_workbook(out_fhand.name, read_only=True)
        ws = workbook.active

        # Check header
        assert ws['A1'].value == "BGV", "Incorrect header value: %s" % (ws['C1'].value)
        assert ws['B1'].value == "Accession", "Incorrect header value: %s" % (ws['B1'].value)
        assert ws['C1'].value == "Fila_F", "Incorrect header value: %s" % (ws['C1'].value)
        assert ws['D1'].value == "Maceta_M", "Incorrect header value: %s" % (ws['D1'].value)
        assert ws['E1'].value == "unique_id", "Incorrect header value: %s" % (ws['E1'].value)
        assert ws['F1'].value == "Caracteristica", "Incorrect header value: %s" % (ws['F1'].value)
        assert ws['G1'].value == "Tipo", "Incorrect header value: %s" % (ws['G1'].value)
        assert ws['H1'].value == "Valor", "Incorrect header value: %s" % (ws['H1'].value)
        assert ws['I1'].value == "Fecha", "Incorrect header value: %s" % (ws['I1'].value)
        assert ws['J1'].value == "Autor", "Incorrect header value: %s" % (ws['J1'].value)
        assert ws['A2'].value == "TRCA0020", "Incorrect plant accession: %s" % (ws['A2'].value)
        assert ws['A21'].value == "TRCA0020", "Incorrect plant accession: %s" % (ws['A21'].value)
        assert ws['A22'].value == "TRPO0020", "Incorrect plant accession: %s" % (ws['A22'].value)
        assert ws['A24'].value == "TRPO0020", "Incorrect plant accession: %s" % (ws['A24'].value)

    def test_create_excel2(self):
        # creates excel
        out_fhand = tempfile.NamedTemporaryFile(suffix='.xlsm')
        write_excel_observations_skeleton(FIELD_REDUCED_FPATH,
                                          NSF1_LEAF_TRAITS_EXCEL,
                                          out_fhand,
                                          accession_header='BGV',
                                          synonym_header='Accession',
                                          row_header='Fila_F',
                                          pot_number_header='Maceta_M',
                                          rows_per_plant=2)

        workbook = load_workbook(out_fhand.name, read_only=True)
        ws = workbook.active

        # Check header
        assert ws['A1'].value == "BGV", "Incorrect header value: %s" % (ws['C1'].value)
        assert ws['B1'].value == "Accession", "Incorrect header value: %s" % (ws['B1'].value)
        assert ws['C1'].value == "Fila_F", "Incorrect header value: %s" % (ws['C1'].value)
        assert ws['D1'].value == "Maceta_M", "Incorrect header value: %s" % (ws['D1'].value)
        assert ws['E1'].value == "unique_id", "Incorrect header value: %s" % (ws['E1'].value)
        assert ws['F1'].value == "Caracteristica", "Incorrect header value: %s" % (ws['F1'].value)
        assert ws['G1'].value == "Tipo", "Incorrect header value: %s" % (ws['G1'].value)
        assert ws['H1'].value == "Valor", "Incorrect header value: %s" % (ws['H1'].value)
        assert ws['I1'].value == "Fecha", "Incorrect header value: %s" % (ws['I1'].value)
        assert ws['J1'].value == "Autor", "Incorrect header value: %s" % (ws['J1'].value)
        assert ws['A21'].value == "TRCA0020", "Incorrect plant accession: %s" % (ws['A21'].value)
        assert ws['A22'].value == "TRPO0020", "Incorrect plant accession: %s" % (ws['A22'].value)
        assert ws['A24'].value == "TRPO0020", "Incorrect plant accession: %s" % (ws['A24'].value)
