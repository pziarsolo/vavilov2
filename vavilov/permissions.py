from django.contrib.auth.models import Permission


VIEW_PERMISIONS = ('View Accession', 'View Passport', 'View Location',
                   'View Accession Relationship', 'View Accession Taxa',
                   'View Assay', 'View Plant', 'View AssayProp',
                   'View Observation', 'View observation images',
                   'View Observation Relationship', 'View Observation entity')


def add_view_permissions(user, filter_perms=None):
    for perm_name in VIEW_PERMISIONS:
        if filter_perms is not None and perm_name in filter_perms:
            continue
        permission = Permission.objects.get(name=perm_name)
        user.user_permissions.add(permission)
