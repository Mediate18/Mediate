from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import json

from catalogues.models import Dataset


def get_dataset_for_user(request):
    """
    Gets the dataset for the current user:
    if a dataset is set in the session and the user has permission to change, return that dataset;
    otherwise return the default dataset
    :param request: the current request object
    :return: dataset
    """
    user = request.user
    dataset = request.session.get('dataset', None)
    if dataset and user.has_perm('catalogues.change_dataset', Dataset.objects.get(uuid=json.loads(dataset)['uuid'])):
        return Dataset.objects.get(uuid=json.loads(dataset)['uuid'])

    return get_dataset_for_anonymoususer()


def get_dataset_for_anonymoususer():
    try:
        return Dataset.objects.get(name=settings.DATASET_NAME_FOR_ANONYMOUSUSER)
    except KeyError:
        return None
    except ObjectDoesNotExist:
        return None
