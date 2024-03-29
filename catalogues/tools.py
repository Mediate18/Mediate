from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import json

from catalogues.models import Dataset


def get_permitted_datasets_for_session(request):
    datasets_session = request.session.get('datasets', [])
    if datasets_session:
        datasets_retrieved = Dataset.objects.filter(uuid__in=[dataset['uuid']
                                                            for dataset in datasets_session])
    else:
        datasets_retrieved = get_dataset_for_anonymoususer()
    datasets_permitted = [dataset for dataset in datasets_retrieved
                          if request.user.has_perm('catalogues.change_dataset', dataset)]
    return datasets_permitted


def get_datasets_for_session(request, extra_dataset=None):
    """
    Gets the dataset for the current user:
    if a dataset is set in the session and the user has permission to change, return that dataset;
    otherwise return the default dataset
    :param request: the current request object
    :return: dataset
    """
    datasets_permitted = get_permitted_datasets_for_session(request)
    if datasets_permitted:
        return datasets_permitted + [extra_dataset] if extra_dataset else datasets_permitted

    return list(get_dataset_for_anonymoususer())


def get_dataset_for_anonymoususer():
    try:
        return Dataset.objects.filter(name=settings.DATASET_NAME_FOR_ANONYMOUSUSER)
    except KeyError:
        return Dataset.objects.none()
