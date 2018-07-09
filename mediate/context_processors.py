from django.conf import settings


def application_instance_type(request):
    return {"APPLICATION_INSTANCE_TYPE": settings.APPLICATION_INSTANCE_TYPE}