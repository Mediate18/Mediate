from django.conf import settings
from django.shortcuts import render


class SetRemoteAddrMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            request.META['REMOTE_ADDR'] = x_forwarded_for.split(',')[0].strip()
        return self.get_response(request)


class OldHostNameWarningMiddleware:
    """
    If an old host name is used, show a warning and an up-to-date URL.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host_name = request.get_host().split(':')[0]
        if host_name == settings.HOST_NAME:
            return self.get_response(request)

        context = {
            'base_url': request.build_absolute_uri('/').replace(host_name, settings.HOST_NAME),
            'new_url': request.build_absolute_uri().replace(host_name, settings.HOST_NAME),
        }
        return render(request, "old_host_name_warning.html", context)