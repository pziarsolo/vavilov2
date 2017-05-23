from django.contrib.auth.models import Permission
from guardian.conf.settings import ANONYMOUS_USER_NAME

PUBLIC_VIEW_PERMISSIONS = ('View Accession', 'View Passport', 'View Location',
                           'View Accession Relationship',
                           'View Accession Taxa')

VIEW_PERMISIONS = PUBLIC_VIEW_PERMISSIONS + ('View Assay', 'View Plant',
                                             'View AssayProp', 'View Trait',
                                             'View Observation', 'View observation images',
                                             'View Observation Relationship',
                                             'View Observation entity')


def add_view_permissions(user, filter_perms=None):
    perms = PUBLIC_VIEW_PERMISSIONS if user.username == ANONYMOUS_USER_NAME else VIEW_PERMISIONS
    for perm_name in perms:
        if filter_perms is not None and perm_name in filter_perms:
            continue
        permission = Permission.objects.get(name=perm_name)
        user.user_permissions.add(permission)
