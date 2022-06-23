from django.contrib.auth.models import Group
from django.conf import settings
from django_registration.signals import user_activated
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist


# TODO: move this to a more appropriate place, e.g. a signals.py file
@receiver(user_activated)
def add_user_to_default_group(sender, user, request, **kwargs):
    try:
        default_group = Group.objects.get(name=settings.GROUP_NAME_FOR_GUEST_ACCOUNTS)
    except ObjectDoesNotExist:
        # TODO: handle the exception better
        print("A group with name '{}' could not be found.".format(settings.GROUP_NAME_FOR_GUEST_ACCOUNTS))
        return

    user.groups.add(default_group)

