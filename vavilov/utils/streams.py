import csv
import logging
from time import time
from django.http.response import StreamingHttpResponse, HttpResponse

from openpyxl import Workbook
from openpyxl.utils.cell import get_column_letter

from vavilov.conf.settings import MAX_OBS_TO_EXCEL, APP_LOGGER
logger = logging.getLogger(APP_LOGGER)


def calc_duration(action, prev_time):
    now = time()
    logger.debug('{}: Took {} secs'.format(action, round(now - prev_time, 2)))
    return now


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


MSG = """<script>
    alert('To much observations( more than {}). Please contact with the admin to obtain the excel file :)');
    window.history.back();
</script>""".format(MAX_OBS_TO_EXCEL)


def return_csv_response(queryset, table_class):
    prev_time = time()
    if queryset.count() > MAX_OBS_TO_EXCEL:
        return HttpResponse(MSG, content_type="text/html")
    prev_time = calc_duration('Csv Query Count', prev_time)
    rows = table_class(queryset).as_values()
    prev_time = calc_duration('table to rows', prev_time)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response


def return_csv_trait_columns(queryset):
    rows = queryset_to_columns(queryset)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response


def queryset_to_columns(queryset):
    traits = sorted(list(queryset.distinct().values_list('trait__name', flat=True)))
    obs_entities = queryset.distinct().values_list('obs_entity__name', flat=True)
    yield ['Accession', 'Observation entity', 'Assay', 'Plant_part'] + traits
    for obs_entity in obs_entities:
        row = []
        row.append(obs_entity.accession)
        row.append(obs_entity.name)
        row.append(obs_entity.assay.name)
        row.append(obs_entity.plant_part.name)
        observations = queryset.filter(obs_entity__name=obs_entity)
        row.extend([':'.join(observations.filter(trait__name=trait).values_list('value', flat=True)) for trait in traits])
        yield row


def return_excel_response(queryset, table_class, column_length=None):
    if queryset.count() > MAX_OBS_TO_EXCEL:
        return HttpResponse(MSG, content_type="text/html")

    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(content_type=content_type)
    rows = table_class(queryset).as_values()
    wb = create_workbook_from_queryset(rows, column_length)
    response['Content-Disposition'] = 'attachment; filename="somefilename.xlsx"'
    wb.save(response)
    return response


def create_excel_from_queryset(out_fpath, queryset, table, column_length=None):
    rows = table(queryset).as_values()
    wb = create_workbook_from_queryset(rows, column_length=column_length)
    wb.save(out_fpath)


def create_workbook_from_queryset(rows, column_length=None):
    wb = Workbook(write_only=True)
    ws = wb.create_sheet()

    if column_length is None:
        column_length = 13
    first = True
    for row in rows:
        if first:
            first = False
            for col_index in range(len(row)):
                column = get_column_letter(col_index + 1)
                ws.column_dimensions[column].width = column_length
        ws.append(row)
    return wb
