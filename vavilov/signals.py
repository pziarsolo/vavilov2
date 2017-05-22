from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from vavilov.permissions import add_view_permissions
from django.contrib.auth.models import Permission, User
from django.core.exceptions import AppRegistryNotReady


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

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
