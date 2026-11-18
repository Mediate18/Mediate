from django.conf import settings

from ninja import NinjaAPI, Query
from ninja.pagination import paginate
from ninja.security import APIKeyHeader

from mediate.api_schemas import PersonSchema, PersonFilterSchema, WorkSchema, WorkFilterSchema
from persons.models import Person
from items.models import Work


api = NinjaAPI(
    title=settings.API_TITLE,
    version="0.0.1",
    description=settings.API_DESCRIPTION,
)


class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        return key == settings.PRINT_ROADS_API_KEY


@api.get(f"/person", response=list[PersonSchema], auth=ApiKey())
@paginate
def person_search(request, filters: Query[PersonFilterSchema]):
    """
    Search for Person entities. The given string is searched for in fields *short name*, *first name* and *birth name*.
    """
    return filters.filter(Person.objects.all())


@api.get(f"/work", response=list[WorkSchema], auth=ApiKey())
@paginate
def work_search(request, filters: Query[WorkFilterSchema]):
    """
    Search for Work entities. The given string is searched for in field *title*.
    """
    return filters.filter(
        Work.objects.prefetch_related(
            'items__item__personitemrelation_set__person',
            'items__item__personitemrelation_set__role',
        )
    )
