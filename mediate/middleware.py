from django.conf import settings
from catalogues.models import Dataset

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
                # Show Dataset select page
                pass
            else:
                # Set default dataset for AnonymousUser
                default_dataset = Dataset.objects.get(name=settings.DATASET_NAME_FOR_ANONYMOUSUSER)
                request.session['dataset'] = str(default_dataset.uuid)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        print('Dataset:', request.session.get('dataset', None))

        return response