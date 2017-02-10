from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Permission
from django.core.exceptions import AppRegistryNotReady


VIEW_PERMISIONS = ('View Accession', 'View Passport', 'View Location',
                   'View Accession Relationship', 'View Accession Taxa',
                   'View Assay', 'View Plant', 'View AssayProp',
                   'View Observation')


def add_view_permissions(user, filter_perms=None):
    for perm_name in VIEW_PERMISIONS:
        if filter_perms is not None and perm_name in filter_perms:
            continue
        permission = Permission.objects.get(name=perm_name)
        user.user_permissions.add(permission)


# All users created have view permission for models.
# Per row permission must be granted
# When we create new user we recevive the signal and give to the user view
# permissions
@receiver(post_save, sender=User)
def add_def_view_perms(sender, instance, **kwargs):
    try:
        add_view_permissions(instance)
    except Permission.DoesNotExist as error:
        if str(error) == 'Permission matching query does not exist.':
            raise AppRegistryNotReady('guardian loaded before vavilov loaded')
        raise