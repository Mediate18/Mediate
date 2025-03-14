import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.db.models import Q
import itertools

from .models import *
from mediate.tools import round_to_n
from mediate.columns import ActionColumn, render_action_column
from catalogues.models import PersonCollectionRelation, Collection, CollectionPlaceRelation
from items.models import PersonItemRelation, Edition
from apiconnectors.cerlapi import cerl_record_url
from django.utils.translation import gettext_lazy as _

from collections import defaultdict


# Person table
class PersonTable(tables.Table):
    uuid = tables.Column(empty_values=(), verbose_name="", orderable=False)
    collections = tables.Column(empty_values=())
    roles = tables.Column(empty_values=())
    viaf_id = tables.Column(empty_values=())
    relations = tables.Column(
        verbose_name=_("Relations"),
        orderable=False,
        empty_values=()
    )

    class Meta:
        model = Person
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'short_name',
            'first_names',
            'surname',
            'sex',
            'roles',
            'city_of_birth',
            'date_of_birth',
            'city_of_death',
            'date_of_death',
            'collections',
            'viaf_id',
            'publisher_cerl_id',
            'notes',
            'bibliography',
            'relations',
            'uuid'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data.data = self.data.data.prefetch_related(
            'city_of_birth',
            'city_of_death',
            'relations_when_first',
            'relations_when_second',
            'personcollectionrelation_set',
            'personcollectionrelation_set__role',
            'works',
            'publisher_set',
            'personitemrelation_set',
            'personitemrelation_set__role',
        )

    def render_uuid(self, record, value):
        url_name_change = 'change_person' if self.request.user.has_perm('persons.change_person') else None
        url_name_delete = 'delete_person' if self.request.user.has_perm('persons.delete_person') else None

        return render_action_column(value, 'person_detail', url_name_change, url_name_delete)

    def render_collections(self, record):
        person_collection_relations = [relation for relation in record.personcollectionrelation_set.all() if relation.role.name == "owner"]
        relation_groups = []
        for role in set([relation.role for relation in person_collection_relations]):
            role_relations = [relation for relation in person_collection_relations if relation.role == role]
            collections = []
            for relation in role_relations:
                collection = relation.collection
                title = collection.short_title
                collection_entry = "<a href='{}'>{}</a>".format(reverse_lazy('collection_detail', args=[collection.pk]), title)
                collections.append(collection_entry)

            relation_groups.append(", ".join(collections))
        return format_html("<br/> ".join(relation_groups))

    def render_roles(self, record):
        roles_dict = {}

        collection_roles = [collection.role.name for collection in record.personcollectionrelation_set.all()]
        if collection_roles:
            roles_dict['collections'] = collection_roles

        # Items
        item_roles = list({item.role.name for item in record.personitemrelation_set.all()})
        if item_roles:
            roles_dict['items'] = item_roles

        # Editions
        editions_count = record.publisher_set.count()
        if editions_count:
            roles_dict['edition'] = ['publisher']

        # Works
        work_count = record.works.count()
        if work_count:
            roles_dict['works'] = ['author']

        text = "<br/>".join(["{}: {}".format(k.capitalize(), ", ".join(v)) for k, v in roles_dict.items()])
        return format_html('<a href="{}">{}</a>'.format(reverse_lazy('person_detail', args=[record.pk]), text))

    def render_viaf_id(self, value):
        if value:
            return format_html('<a target="blank" href="{}">{}</a>'.format(
                value, value
            ))
        else:
            return format_html('-')

    def render_publisher_cerl_id(self, value):
        if value:
            url = cerl_record_url + value
            return format_html('<a target="blank" href="{}">{}</a>'.format(
                url, value
            ))
        else:
            return format_html('-')

    def render_relations(self, record):
        person = record
        of_str = ' of'
        relations = []
        for relation in person.relations_when_first.all():
            relation_of_str = '' if relation.type.name.endswith(of_str) else of_str
            relation_str = format_html(_('{}{} <a href="{}">{}</a>'), str(relation.type).capitalize(), relation_of_str,
                                     relation.second_person.get_absolute_url(), relation.second_person)
            relations.append(relation_str)
        for relation in person.relations_when_second.all():
            type = str(relation.type)
            type_without_of = type[:-len(of_str)] if type.endswith(of_str) else type
            relation_str = format_html(_('{}: <a href="{}">{}</a>'), type_without_of.capitalize(),
                                     relation.first_person.get_absolute_url(), relation.first_person)
            relations.append(relation_str)
        return format_html_join('\n', '{}<br/>', ((rel,) for rel in relations))



# PersonRanking table
class PersonRankingTable(PersonTable):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))
    collection_count = tables.Column(empty_values=(), verbose_name=_("# collections"))

    class Meta:
        model = Person
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'item_count',
            'collection_count',
            'short_name',
            'first_names',
            'surname',
            'sex',
            'roles',
            'city_of_birth',
            'date_of_birth',
            'city_of_death',
            'date_of_death',
            'collections',
            'viaf_id',
            '...',
            'uuid'
        ]
        
    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)


class PersonWeightedRankingTable(PersonRankingTable):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    weight = tables.Column(empty_values=(), verbose_name="Percentage of collections (precalculated)")
    dynamic_weight = tables.Column(empty_values=(), verbose_name="Percentage of collections (dynamic)")
    collection_count = tables.Column(empty_values=())
    potential_collection_count = tables.Column(empty_values=())

    class Meta:
        model = Person
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'weight',
            'dynamic_weight',
            'collection_count',
            'potential_collection_count',
            'short_name',
            'first_names',
            'surname',
            'sex',
            'roles',
            'city_of_birth',
            'date_of_birth',
            'city_of_death',
            'date_of_death',
            'collections',
            'viaf_id',
            '...',
            'uuid'
        ]

    def render_weight(self, value):
        if not value:
            return '-'
        new_value = round(value) if value > 10.0 else round_to_n(value, 2) if value != 0.0 else value
        return f'{new_value}%'

    def render_dynamic_weight(self, value):
        if not value:
            return '-'
        new_value = round(value) if value > 10.0 else round_to_n(value, 2) if value != 0.0 else value
        return f'{new_value}%'


# PersonPersonRelation table
class PersonPersonRelationTable(tables.Table):
    uuid = ActionColumn('personpersonrelation_detail', 'change_personpersonrelation', 'delete_personpersonrelation',
                        orderable=False)

    class Meta:
        model = PersonPersonRelation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'first_person',
            'second_person',
            'type',
            'start_year',
            'end_year',
            'uuid'
        ]


# PersonPersonRelationType table
class PersonPersonRelationTypeTable(tables.Table):
    uuid = ActionColumn('personpersonrelationtype_detail', 'change_personpersonrelationtype',
                        'delete_personpersonrelationtype', orderable=False)

    class Meta:
        model = PersonPersonRelationType
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'directed',
            'uuid'
        ]


# PersonProfession table
class PersonProfessionTable(tables.Table):
    uuid = ActionColumn('personprofession_detail', 'change_personprofession', 'delete_personprofession',
                        orderable=False)

    class Meta:
        model = PersonProfession
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'profession',
            'uuid'
        ]


# Country table
class CountryTable(tables.Table):
    uuid = ActionColumn('country_detail', 'change_country', 'delete_country',
                        orderable=False)

    class Meta:
        model = Country
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'uuid'
        ]


# Country table
class CountryRankingTable(CountryTable):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))
    collection_count = tables.Column(empty_values=(), verbose_name=_("# collections"))

    class Meta:
        model = Country
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'item_count',
            'collection_count',
            'name',
            'uuid'
        ]

    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)


# Place table
class PlaceTable(tables.Table):
    uuid = ActionColumn('place_detail', 'change_place', 'delete_place',
                        orderable=False)

    class Meta:
        model = Place
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'cerl_id',
            'country',
            'longitude',
            'latitude',
            'uuid'
        ]
        
        
# PlaceRanking table
class PlaceRankingTable(PlaceTable):
    row_index = tables.Column(empty_values=(), orderable=False, verbose_name="")
    item_count = tables.Column(empty_values=(), verbose_name=_("# items"))
    collection_count = tables.Column(empty_values=(), verbose_name=_("# collections"))
    person_count = tables.Column(empty_values=(), verbose_name=_("# persons"))

    class Meta:
        model = Place
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'row_index',
            'item_count',
            'collection_count',
            'person_count',
            'name',
            'cerl_id',
            'country',
            'longitude',
            'latitude',
            'uuid'
        ]

    def __init__(self, *args, **kwargs):
        filter = kwargs.pop('filter', None)
        super().__init__(*args, **kwargs)
        self.year = filter.get_year_range()
        self.collections = filter.get_collections()

    def render_row_index(self):
        self.row_index = getattr(self, 'row_index', itertools.count(self.page.start_index()))
        return next(self.row_index)

    def render_person_count(self, record):
        collections_query = Q(personitemrelation__item__lot__collection__in=self.collections) if self.collections else Q()
        if self.year:
            year = self.year
            if year[0] and year[1]:
                return Person.objects\
                    .filter(Q(residence__place=record, residence__start_year__gte=year[0], residence__end_year__lte=year[1])
                            | Q(city_of_birth=record, date_of_birth__gte=year[0], date_of_birth__lte=year[1])
                            | Q(city_of_death=record, date_of_death__gte=year[0], date_of_death__lte=year[1])) \
                    .filter(collections_query).distinct().count()
            elif year[0]:
                return Person.objects \
                    .filter(Q(residence__place=record, residence__start_year__gte=year[0])
                            | Q(city_of_birth=record, date_of_birth__gte=year[0])
                            | Q(city_of_death=record, date_of_death__gte=year[0])) \
                    .filter(collections_query).distinct().count()
            elif year[1]:
                return Person.objects \
                    .filter(
                    Q(residence__place=record, residence__end_year__lte=year[1])
                    | Q(city_of_birth=record, date_of_birth__lte=year[1])
                    | Q(city_of_death=record, date_of_death__lte=year[1])) \
                    .filter(collections_query).distinct().count()

        # Default
        return Person.objects.filter(Q(residence__place=record) | Q(city_of_birth=record) | Q(city_of_death=record))\
                .filter(collections_query) \
                .distinct().count()


# Place links table
class PlaceLinksTable(tables.Table):
    uuid = ActionColumn('place_detail', 'change_place', 'delete_place',
                        orderable=False)
    collections = tables.Column(empty_values=(), verbose_name="Collections",
                        orderable=False)
    editions = tables.Column(empty_values=(), verbose_name="Editions",
                        orderable=False)
    people_born = tables.Column(empty_values=(), verbose_name="People born",
                        orderable=False)
    people_died = tables.Column(empty_values=(), verbose_name="People died",
                        orderable=False)
    residences = tables.Column(empty_values=(), verbose_name="People inhabiting",
                        orderable=False)

    class Meta:
        model = Place
        attrs = {'class': 'table table-sortable'}
        fields = [
            'name',
            'collections',
            'editions',
            'people_born',
            'people_died',
            'residences',
            'uuid'
        ]

    def render_collections(self, record):
        relations = CollectionPlaceRelation.objects.filter(place=record).prefetch_related('type')
        type_dict = defaultdict(list)
        for relation in relations:
            type_dict[relation.type.name].append(relation.collection)

        return format_html("<br/>".join([
            type.capitalize() + ": " + ", ".join([
                '<a href="{}">{}</a>'.format(reverse_lazy('collection_detail', args=[collection.pk]), collection)
                for collection in collections
            ]) for type, collections in type_dict.items()
        ]))

    def render_editions(self, record):
        editions = Edition.objects.filter(place=record)
        return format_html(", ".join(
            ['<a href="{}">{}</a>'.format(reverse_lazy('edition_detail', args=[edition.pk]),
                                          edition)
                for edition in editions]
        ))

    def render_people_born(self, record):
        persons = Person.objects.filter(city_of_birth=record)
        return format_html(", ".join(
            ['<a href="{}">{}</a>'.format(reverse_lazy('person_detail', args=[person.pk]),
                                          person)
                for person in persons]
        ))

    def render_people_died(self, record):
        persons = Person.objects.filter(city_of_death=record)
        return format_html(", ".join(
            ['<a href="{}">{}</a>'.format(reverse_lazy('person_detail', args=[person.pk]),
                                          person)
                for person in persons]
        ))

    def render_residences(self, record):
        persons = Person.objects.filter(residence__place=record)
        return format_html(", ".join(
            ['<a href="{}">{}</a>'.format(reverse_lazy('person_detail', args=[person.pk]),
                                          person)
                for person in persons]
        ))


# Profession table
class ProfessionTable(tables.Table):
    uuid = ActionColumn('profession_detail', 'change_profession', 'delete_profession', orderable=False)

    class Meta:
        model = Profession
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'description',
            'uuid'
        ]


# Religion table
class ReligionTable(tables.Table):
    uuid = ActionColumn('religion_detail', 'change_religion', 'delete_religion', orderable=False)

    class Meta:
        model = Religion
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'name',
            'description',
            'uuid'
        ]


# ReligiousAffiliation table
class ReligiousAffiliationTable(tables.Table):
    uuid = ActionColumn('religiousaffiliation_detail', 'change_religiousaffiliation', 'delete_religiousaffiliation',
                        orderable=False)

    class Meta:
        model = ReligiousAffiliation
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'religion',
            'uuid'
        ]


# Residence table
class ResidenceTable(tables.Table):
    uuid = ActionColumn('residence_detail', 'change_residence', 'delete_residence',
                        orderable=False)

    class Meta:
        model = Residence
        attrs = {'class': 'table table-sortable'}
        sequence = [
            'person',
            'place',
            'start_year',
            'end_year',
            'uuid'
        ]


