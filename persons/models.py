from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_date_extensions.fields import ApproximateDateField
from django.urls import reverse_lazy

from computedfields.models import ComputedFieldsModel, computed
from simple_history.models import HistoricalRecords

import requests

import mediate.tools
from apiconnectors.cerlapi import cerl_record_url_api

import uuid

from simplemoderation.tools import moderated


class Country(models.Model):
    """
    A country
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the place"), max_length=128, null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('country_detail', args=[str(self.uuid)])


class Place(models.Model):
    """
    A geographical place
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the place"), max_length=128, null=True)
    cerl_id = models.CharField(_("CERL ID of a place"), max_length=32, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse_lazy('place_detail', args=[str(self.uuid)])

    def get_lat_long(self, overwrite=False):
        if self.cerl_id and (overwrite or (not self.latitude or not self.longitude)):
            response = requests.get(cerl_record_url_api + self.cerl_id, headers={'accept': 'application/json'})
            cerl_record_json = response.json()
            try:
                if overwrite or not self.latitude:
                    self.latitude = cerl_record_json['data']['location']['point']['lat']
            except KeyError:
                pass
            try:
                if overwrite or not self.longitude:
                    self.longitude = cerl_record_json['data']['location']['point']['long']
            except KeyError:
                pass

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.get_lat_long()
        super().save(force_insert=False, force_update=False, using=None,
             update_fields=None)


class Religion(models.Model):
    """
    Religion
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Religion name"), max_length=128)
    description = models.TextField(_("Religion description"))

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


@moderated()
class Person(ComputedFieldsModel):
    """
    A person
    """

    # Sex choices
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'
    UNKNOWN = 'UNKNOWN'
    CORPORATE = 'CORPRT'
    SEX_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
        (UNKNOWN, 'Unknown'),
        (CORPORATE, 'Corporate')
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_name = models.CharField(_("Short name"), max_length=128, null=True)
    viaf_id = models.CharField(_("VIAF ID (https://viaf.org)"), max_length=128, null=True, blank=True)
    publisher_cerl_id = models.CharField(_("Publisher CERL ID"), max_length=32, null=True, blank=True)
    surname = models.CharField(_("Surname"), max_length=128)
    first_names = models.CharField(_("First names"), max_length=512)
    date_of_birth = models.CharField(_("Date of birth"), max_length=64, blank=True, null=True)
    date_of_death = models.CharField(_("Date of death"), max_length=64, blank=True, null=True)
    sex = models.CharField(_("Sex"), choices=SEX_CHOICES, max_length=7)
    city_of_birth = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='persons_born')
    city_of_death = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='persons_died')
    notes = models.TextField(_("Notes"), null=True, blank=True)
    bibliography = models.TextField(_("Bibliography"), null=True, blank=True)

    history = HistoricalRecords(bases=[ComputedFieldsModel], excluded_fields=['weight', 'earliest_edition_year'])

    @computed(models.SmallIntegerField(null=True), depends=[('self', ['date_of_birth'])])
    def normalised_date_of_birth(self):
        return mediate.tools.date_of_x_text_to_int(self.date_of_birth)

    @computed(models.SmallIntegerField(null=True), depends=[('self', ['date_of_death'])])
    def normalised_date_of_death(self):
        return mediate.tools.date_of_x_text_to_int(self.date_of_death)

    @computed(models.FloatField(null=True), depends=[('personitemrelation_set.item.edition', ['year_start']),
                                                     ('personitemrelation_set.item.lot', ['collection'])])
    def weight(self):
        from items.models import Edition  # TODO circular import
        from catalogues.models import Collection  # TODO circular import
        earliest_edition = (Edition.objects.filter(items__personitemrelation__person=self, year_start__isnull=False)
                            .order_by('year_start').first())
        if not earliest_edition:
            return None
        collections = Collection.objects.filter(catalogue__dataset__name=settings.DATASET_NAME_FOR_ANONYMOUSUSER)
        collection_count = collections.filter(lot__item__personitemrelation__person=self).distinct().count()
        potential_collection_count = (collections.filter(year_of_publication__gte=earliest_edition.year_start).
                                      distinct().count())
        if not potential_collection_count:
            return None
        return 100 * collection_count / potential_collection_count

    @computed(models.IntegerField(null=True), depends=[('personitemrelation_set.item.edition', ['year_start']),
                                                     ('personitemrelation_set.item.lot', ['collection'])])
    def earliest_edition_year(self):
        from items.models import Edition  # TODO circular import
        if earliest_edition := (Edition.objects.filter(items__personitemrelation__person=self, year_start__isnull=False)
                .order_by('year_start').first()):
            return earliest_edition.year_start
        return None

    class Meta:
        ordering = ['short_name']
        indexes = [
            models.Index(fields=["weight"], name="weight_idx"),
            models.Index(fields=["earliest_edition_year"], name="earliest_edition_year_idx"),
        ]

    def __str__(self):
        return self.short_name

    def get_absolute_url(self):
        return reverse_lazy('person_detail', args=[str(self.uuid)])


class AlternativePersonName(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='alternative_names')
    short_name = models.CharField(_("Short name"), max_length=128, null=True)
    surname = models.CharField(_("Surname"), max_length=128)
    first_names = models.CharField(_("First names"), max_length=512)

    def __str__(self):
        return self.short_name


class ReligiousAffiliation(models.Model):
    """
    Religious affiliation of a person
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    religion = models.ForeignKey(Religion, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('person', 'religion'),)

    def __str__(self):
        return _("{} is affiliated to {}").format(self.person, self.religion)


class Residence(models.Model):
    """
    The residence of a person for a period of time
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    start_year = models.IntegerField(_("Start year of interval"), null=True)
    end_year = models.IntegerField(_("End year of inter"), null=True)

    class Meta:
        unique_together = (('person', 'place', 'start_year', 'end_year'),)

    def __str__(self):
        object_str = _("{} lived in {}").format(self.person, self.place)
        if self.start_year:
            object_str = object_str + _(" from {}").format(self.start_year)
        if self.end_year:
            object_str = object_str + _(" until {}").format(self.end_year)
        return object_str


class Profession(models.Model):
    """
    Profession
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Profession name"), max_length=128)
    description = models.TextField(_("Profession description"), blank=True)

    def __str__(self):
        return self.name


class PersonProfession(models.Model):
    """
    Person-profession relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    def __str__(self):
        return _("Profession of {} is {}").format(self.person.short_name, self.profession.name)


class PersonPersonRelationType(models.Model):
    """
    Person-person relation type, e.g.
    * family relation
      - spouse (NOT directed)
      - child (directed)
    * professional relation
      - partner (NOT directed)
      - employee (directed)
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Relation type name"), max_length=128)
    directed = models.BooleanField(_("Directed"), default=False)

    def __str__(self):
        return self.name



class PersonPersonRelation(models.Model):
    """
    Person-person relation
    <first_person> is <type> <second_person> [from <start_year>] [until <end_year>]
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="relations_when_first")
    second_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="relations_when_second")
    type = models.ForeignKey(PersonPersonRelationType, on_delete=models.PROTECT)
    start_year = models.IntegerField(_("Start year of interval"), null=True)
    end_year = models.IntegerField(_("End year of inter"), null=True)

    def clean(self):
        # TODO Check that the relation is not duplicated is some way
        pass

    def __str__(self):
        object_str = _("{} is {} of {}").format(self.first_person, self.type, self.second_person)
        if self.start_year:
            object_str = object_str + _(" from {}").format(self.start_year)
        if self.end_year:
            object_str = object_str + _(" until {}").format(self.end_year)
        return object_str


# Enable the simple-history registration:
from .history import *


# Clear cache when a model object is saved
from django.db.models.signals import post_save, post_delete
from mediate.tools import receiver_with_multiple_senders
from django.core.cache import cache


@receiver_with_multiple_senders([post_save, post_delete],[
    Country, Place, Religion, Person, AlternativePersonName, ReligiousAffiliation, Residence, Profession,
    PersonProfession, PersonPersonRelationType, PersonPersonRelation
])
def clear_cache(sender, instance, **kwargs):
    cache.clear()