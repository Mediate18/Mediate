from typing import Annotated
from uuid import UUID

from ninja import ModelSchema, FilterSchema, FilterLookup, Schema
from pydantic import Field

from persons.models import Place, Person
from items.models import Work, PersonItemRelation, PersonItemRelationRole


class UrlSchema(Schema):
    url: str

    @staticmethod
    def resolve_url(obj, context) -> str:
        request = context["request"]
        return f'{request.scheme}://{request.get_host()}{obj.get_absolute_url()}'


class PlaceSchema(UrlSchema, ModelSchema):
    id: UUID = Field(..., alias="uuid")

    class Meta:
        model = Place
        fields = ["name"]


class PersonSchema(UrlSchema, ModelSchema):
    id: UUID = Field(..., alias="uuid")
    city_of_birth: PlaceSchema | None
    city_of_death: PlaceSchema | None

    class Meta:
        model = Person
        fields = ["short_name", "sex", "city_of_birth", "date_of_birth", "city_of_death", "date_of_death"]


class PersonFilterSchema(FilterSchema):
    search: Annotated[
        str | None,
        FilterLookup(["short_name__icontains", "first_names__icontains", "birth_name__icontains", "surname__icontains"]),
    ] = None


class CompactPersonSchema(UrlSchema, ModelSchema):
    id: UUID = Field(..., alias="uuid")

    class Meta:
        model = Person
        fields = ["short_name", "sex", "date_of_birth", "date_of_death"]


class RoleSchema(ModelSchema):
    id: UUID = Field(..., alias="uuid")

    class Meta:
        model = PersonItemRelationRole
        fields = ["name"]


class PersonItemRelationSchema(ModelSchema):
    person: CompactPersonSchema
    role: RoleSchema

    class Meta:
        model = PersonItemRelation
        fields = ["person", "role"]


class WorkSchema(UrlSchema, ModelSchema):
    id: UUID = Field(..., alias="uuid")
    related_persons: list[PersonItemRelationSchema]

    class Meta:
        model = Work
        fields = ["title"]

    @staticmethod
    def resolve_related_persons(work: Work) -> list[PersonItemRelationSchema]:
        personitemrelations = [personitemrelation
                    for itemwork in work.items.all()
                    for personitemrelation in itemwork.item.personitemrelation_set.all()]

        # Make distinct by person+role
        person_roles = set()
        personitemrelation_list = []
        for relation in personitemrelations:
            if (relation.person_id, relation.role_id) not in person_roles:
                person_roles.add((relation.person_id, relation.role_id))
                personitemrelation_list.append(relation)

        return personitemrelation_list



class WorkFilterSchema(FilterSchema):
    search: Annotated[str | None, FilterLookup(["title__icontains"]),] = None
