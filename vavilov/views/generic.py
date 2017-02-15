import logging
from time import time

from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.views.generic.base import View

from django_tables2.config import RequestConfig

from vavilov.utils.csv import return_csv_response
from vavilov.utils.streams import return_excel_response
from vavilov.conf.settings import APP_LOGGER


logger = logging.getLogger(APP_LOGGER)


def search_criteria_to_get_parameters(search_criteria):
    get_params = ''
    for key, value in search_criteria.items():
        if isinstance(value, list):
            for val in value:
                get_params += "&{}={}".format(key, val)
        else:
            get_params += "&{}={}".format(key, value)
    return get_params


def calc_duration(action, prev_time):
    now = time()
    logger.debug('{}: Took {} secs'.format(action, round(now - prev_time, 2)))
    return now


class SearchListView(View):
    model = None
    template_name = ''
    form_class = None
    table = None
    redirect_in_one = True
    detail_view_name = ''

    def post(self, request):
        return self._search_and_list(request, method='post')

    def get(self, request):
        return self._search_and_list(request, method='get')

    def _search_and_list(self, request, method):
        getdata = False
        if method == 'get':
            form = self.form_class(self.request.GET or None)
            getdata = True if request.GET else False
        else:
            form = self.form_class(self.request.POST or None)
        if form.is_valid():
            search_criteria = form.cleaned_data
            search_criteria = dict([(key, value) for key, value in
                                    search_criteria.items() if value])
            self.object_list = self.get_queryset(search_criteria=search_criteria,
                                                 user=request.user)
        else:
            self.object_list = self.model.objects.none()
            search_criteria = None
        if getdata:
            criteria = search_criteria_to_get_parameters(search_criteria)
        else:
            criteria = None

        download_search = request.GET.get('download_search', False)
        if method == 'get' and download_search:
            format_ = request.GET['format']
            if format_ == 'csv':
                return return_csv_response(self.object_list, self.table)
            elif format_ == 'excel':
                return return_excel_response(self.object_list, self.table)

        if self.detail_view_name and self.object_list.count() == 1:
            return redirect(self.object_list.first().get_absolute_url())

        return render_to_response(self.template_name,
                                  self.get_context_data(form=form,
                                                        criteria=criteria,
                                                        search_criteria=search_criteria,
                                                        getdata=getdata))

    def get_context_data(self, form, criteria, search_criteria, getdata):
        context = RequestContext(self.request)
        if criteria is not None:
            context['criteria'] = criteria
        context['search_criteria'] = search_criteria
        context['form'] = form
        context['getdata'] = getdata
        context.update(csrf(self.request))

        prev_time = time()
        if self.object_list:
            prev_time = calc_duration('Check Query exists', prev_time)
            table = self.table(self.object_list, template='table.html')
            prev_time = calc_duration('Table creation', prev_time)
            RequestConfig(self.request).configure(table)
            prev_time = calc_duration('RequestConfig configure', prev_time)
            object_list = table
        else:
            object_list = None
        context['object_list'] = object_list

        return context

    def get_queryset(self, **kwargs):
        raise NotImplementedError()
