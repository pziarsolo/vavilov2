import copy
from django.contrib.auth.models import Permission

from guardian.conf.settings import ANONYMOUS_USER_NAME

from vavilov.conf.settings import BY_OBJECT_OBS_PERM, ACCESSIONS_ARE_PUBLIC

if BY_OBJECT_OBS_PERM:
    from guardian.mixins import PermissionRequiredMixin
else:
    from django.contrib.auth.mixins import PermissionRequiredMixin

PUBLIC_VIEW_PERMISSIONS = ['View Accession', 'View Passport', 'View Location',
                           'View Accession Relationship',
                           'View Accession Taxa']

VIEW_PERMISIONS = PUBLIC_VIEW_PERMISSIONS + ['View Assay', 'View Plant',
                                             'View AssayProp', 'View Trait',
                                             'View Observation', 'View observation images',
                                             'View Observation Relationship',
                                             'View Observation entity']


def add_view_permissions(user, filter_perms=None):
    if user.username == ANONYMOUS_USER_NAME:
        perms = copy.copy(PUBLIC_VIEW_PERMISSIONS)
        if not ACCESSIONS_ARE_PUBLIC:
            perms.pop(perms.index('View Accession'))

    else:
        perms = VIEW_PERMISIONS

    for perm_name in perms:
        if filter_perms is not None and perm_name in filter_perms:
            continue
        permission = Permission.objects.get(name=perm_name)
        user.user_permissions.add(permission)
