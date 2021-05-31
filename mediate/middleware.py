from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from catalogues.models import Dataset
from mediate.forms import SelectDatasetForm
from catalogues.models import Dataset

import json

class DatasetMiddleware:
    """
    Middleware to make the user choose a Dataset before handling data
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        dataset = request.session.get('dataset', None)
        if not dataset:
            if request.user.is_authenticated:
                if request.path == reverse_lazy('select_dataset'):
                    # Don't change anything to the request - response cycle
                    response = self.get_response(request)
                    return response
                if request.path != reverse_lazy('logout') and not request.is_ajax():
                    # Show Dataset select page
                    return redirect(reverse_lazy('select_dataset'))
            else:
                # Set default dataset for AnonymousUser
                default_dataset = Dataset.objects.get(name=settings.DATASET_NAME_FOR_ANONYMOUSUSER)
                request.session['dataset'] = json.dumps({'uuid': str(default_dataset.uuid),
                                                         'name': default_dataset.name})

        response = self.get_response(request)
        return response