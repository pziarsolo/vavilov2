from django.http.response import Http404

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.compat import is_authenticated

from guardian.utils import get_anonymous_user


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        action = view.action
        if action in ('list', 'create'):
            return request.user.is_authenticated() and request.user.is_staff
        elif action in ('retrieve', 'update', 'partial_update', 'destroy',
                        'set_password'):
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        action = view.action

        if action == 'retrieve':
            return request.user.is_authenticated() and (obj == request.user or request.user.is_staff)
        elif action in ['update', 'partial_update', 'set_password']:
            return request.user.is_authenticated() and (obj == request.user or request.user.is_staff)
        elif action == 'destroy':
            return request.user.is_authenticated() and request.user.is_staff
        else:
            return False


class CustomModelPermissions(BasePermission):
    """
    Is a small modification of the DjangoModelPermissions. In this class we use
    guardians anonUser when user is not autenticated.

    The request is authenticated using `django.contrib.auth` permissions.
    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions

    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete` permissions on the model.

    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """

    # Map methods into required permission codes.
    # Override this if you need to also provide 'view' permissions,
    # or if you want to provide custom permission codes.
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        return [perm % kwargs for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
        else:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply DjangoModelPermissions on a view that '
            'does not set `.queryset` or have a `.get_queryset()` method.'
        )
        user = request.user if request.user.is_authenticated() else get_anonymous_user()
        perms = self.get_required_permissions(request.method, queryset.model)
#         print(user, is_authenticated(user), user.has_perms(perms), perms)
#         print((user and
#                 (is_authenticated(user) or not self.authenticated_users_only) and
#                 user.has_perms(perms)
#                 ))
        return (user and
                (is_authenticated(user) or not self.authenticated_users_only) and
                user.has_perms(perms)
                )


class CustomObjectPermissions(CustomModelPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def get_required_object_permissions(self, method, model_cls):
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        return [perm % kwargs for perm in self.perms_map[method]]

    def has_object_permission(self, request, view, obj):
        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
        else:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply DjangoObjectPermissions on a view that '
            'does not set `.queryset` or have a `.get_queryset()` method.'
        )

        model_cls = queryset.model
        user = request.user if request.user.is_authenticated() else get_anonymous_user()
        perms = self.get_required_object_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):

            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not user.has_perms(read_perms, obj):
                raise Http404

            # Has read permissions.
            return False

        return True


class IsStaffOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )
