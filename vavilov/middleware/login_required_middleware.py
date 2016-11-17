'''
Created on 11/04/2011

@author: jose
'''

import re

from django.conf import settings
from django.http import HttpResponseRedirect

ALLOW = 0
RESTRICT = 1


class LoginRequiredMiddleware:
    '''Middleware that requires for some urls a user to be authenticated'''

    def __init__(self):
        login_exempt_urls, login_require_urls = None, None
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            login_exempt_urls = [re.compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

        if hasattr(settings, 'LOGIN_REQUIRED_URLS'):
            login_require_urls = [re.compile(expr) for expr in settings.LOGIN_REQUIRED_URLS]

        class_name = self.__class__.__name__
        if not login_exempt_urls and not login_require_urls:
            raise ValueError('To use this %s middleware you should provide the LOGIN_EXEMPT_URLS or LOGIN_REQUIRED_URLS' % class_name)
        if login_exempt_urls and login_require_urls:
            raise ValueError('Either LOGIN_EXEMPT_URLS or LOGIN_REQUIRED_URLS should be provided, not both' % class_name)

        self._policy_if_match = ALLOW if login_exempt_urls else RESTRICT
        self._urls = login_exempt_urls if login_exempt_urls else login_require_urls

        # we always have to allow the login url
        login_url = re.compile(settings.LOGIN_URL[1:])
        unauthorized_url = re.compile(settings.UNAUTHORIZED_URL[1:])
        if self._policy_if_match == ALLOW:
            self._urls.append(login_url)
            self._urls.append(unauthorized_url)

    def process_request(self, request):
        msg = "The Login Required middleware requires authentication "
        msg += "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
        msg += "setting to insert 'django.contrib.auth.middlware.AuthenticationMiddleware'. "
        msg += "If that doesn't work, ensure your TEMPLATE_CONTEXT_PROCESSORS "
        msg += "setting includes 'django.core.context_processors.auth'."
        assert hasattr(request, 'user'), msg
        path = request.path_info.lstrip('/')
        path_in_urls = any(url.match(path) for url in self._urls)

        if (path_in_urls and self._policy_if_match == ALLOW or
            not path_in_urls and self._policy_if_match == RESTRICT):
            pass
        elif (not path_in_urls and self._policy_if_match == ALLOW or
             path_in_urls and self._policy_if_match == RESTRICT):
            if not request.user.is_authenticated():
                return HttpResponseRedirect('%s?next=%s' % (settings.UNAUTHORIZED_URL, request.path))
        else:
            raise RuntimeError('Please fix me.')
