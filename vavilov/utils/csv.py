import csv

from django.utils.html import strip_tags
from django.http.response import StreamingHttpResponse


def queryset_to_csv(queryset, table_class):
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


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def return_csv_response(queryset, table_class):
    rows = queryset_to_csv(queryset, table_class)
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter='\t',
                        quoting=csv.QUOTE_NONE)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response
