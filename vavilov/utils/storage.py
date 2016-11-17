from urllib.parse import urljoin, quote_plus

from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class OnlyScanStorage(FileSystemStorage):
    def _save(self, name, content):
        return name

    def get_valid_name(self, name):
        return name

    def get_available_name(self, name, max_length=None):
        return name

    def url(self, name):
        url_ = name.replace(self.location, '').lstrip('/')
        url_ = urljoin(self.base_url, url_)
        return quote_plus(url_, safe='/')
