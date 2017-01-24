import csv

from django.http.response import StreamingHttpResponse, HttpResponse
from django.utils.html import strip_tags
from xlsxwriter.workbook import Workbook
from vavilov.conf.settings import MAX_OBS_TO_EXCEL


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
    if queryset.count() > MAX_OBS_TO_EXCEL:
        return HttpResponse(MSG, content_type="text/html")

    rows = queryset_to_row(queryset, table_class)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=',',
                        quoting=csv.QUOTE_MINIMAL)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response


def return_excel_response(queryset, table_class):
    if queryset.count() > MAX_OBS_TO_EXCEL:
        return HttpResponse(MSG, content_type="text/html")

    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(content_type=content_type)
    create_excel_from_queryset(response, queryset, table_class, in_memory=True)
    response['Content-Disposition'] = 'attachment; filename="somefilename.xlsx"'
    return response


def queryset_to_row(queryset, table_class):
    entries = table_class(queryset)

    header = [field.verbose_name for field in entries.base_columns.values()]
    yield(header)
    for row in entries.rows:
        row_cells = []
        for _, cell in row.items():
            if isinstance(cell, str):
                cell = strip_tags(cell)
            else:
                cell = str(cell)
            row_cells.append(cell)
        yield row_cells


def create_excel_from_queryset(out_fhand, queryset, table, in_memory=False):
    workbook = Workbook(out_fhand, {'in_memory': in_memory})

    worksheet = workbook.add_worksheet()
    max_lengths = {}
    for idx, row in enumerate(queryset_to_row(queryset, table)):
        for col_idx, cell in enumerate(row):
            if col_idx not in max_lengths:
                max_lengths[col_idx] = []
            max_lengths[col_idx].append(len(cell))
        worksheet.write_row(idx, 0, row)
    for col_index, lengths in max_lengths.items():
        length = max(lengths)
        worksheet.set_column(col_index, col_index, length + 2)
    workbook.close()
    return out_fhand
