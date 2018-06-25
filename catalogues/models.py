from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

import uuid

from persons.models import Person
from transcriptions.models import Transcription


class Collection(models.Model):
    """
    The collection a catalogue belongs to
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('change_collection', args=[str(self.uuid)])


class CollectionYear(models.Model):
    """
    The recorded year of a collection
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField(_("Year"))
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.collection, self.year)


class CatalogueType(models.Model):
    """
    The type of a catalogue
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the catalogue type"), max_length=128, null=True)

    def __str__(self):
        return self.name


class Library(models.Model):
    """
    Library or institute that may hold one or more catalogues
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("The name of the library/institute"), max_length=128)

    class Meta:
        verbose_name_plural = "libraries"

    def __str__(self):
        return self.name


class Catalogue(models.Model):
    """
    The catalogue an item occurs in
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transcription = models.ForeignKey(Transcription, on_delete=SET_NULL, null=True)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    full_title = models.TextField(_("Full title"), null=True)
    preface_and_paratexts = models.TextField(_("Preface or prefatory / concluding text"), null=True)
    type = models.ForeignKey(CatalogueType, on_delete=CASCADE, null=True)
    year_of_publication = models.IntegerField(_("Year of publication"), null=True)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    notes = models.TextField(_("Notes for the Mediate project"), null=True)
    bibliography = models.TextField(_("Bibliography"), null=True)
    collection = models.ForeignKey(Collection, on_delete=SET_NULL, null=True)

    class Meta:
        ordering = ['year_of_publication', 'short_title']

    def __str__(self):
        return "{0}".format(self.short_title)

    def get_absolute_url(self):
        return reverse_lazy('change_catalogue', args=[str(self.uuid)])


class CatalogueHeldBy(models.Model):
    """
    A library/institute where a catalogue is held 
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)

    def __str__(self):
        return _("{} held by {}").format(self.catalogue, self.library)


class Lot(models.Model):
    """
    Catalogue lot
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE, null=True)
    bookseller_category_books = models.TextField(_("Heading / category used to describe books"))
    bookseller_category_non_books = models.TextField(_("Heading / category for other, non-book items"))
    number_in_catalogue = models.CharField(_("Number of items as listed in catalogue"), max_length=128)
    item_as_listed_in_catalogue = models.TextField(_("Full item description, exactly as in the catalogue"))

    class Meta:
        ordering = ['catalogue__year_of_publication', 'catalogue__short_title', 'item_as_listed_in_catalogue']

    def __str__(self):
        return self.item_as_listed_in_catalogue

    def get_absolute_url(self):
        return reverse_lazy('change_lot', args=[str(self.uuid)])


class PersonCollectionRelation(models.Model):
    """
    A person-collection relation (i.e. collector)
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    collection = models.ForeignKey(Collection, on_delete=CASCADE)

    class Meta:
        unique_together = (("person", "collection"),)  # Multiple identical relation would be redundant

    def __str__(self):
        return _("{} is collector of {}").format(self.person, self.collection)


class PersonCatalogueRelationRole(models.Model):
    """
    A type for a person-catalogue relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Role name for a person-catalogue relation"), max_length=128)

    def __str__(self):
        return self.name


class PersonCatalogueRelation(models.Model):
    """
    A person-catalogue item relation (e.g. author, translator, illustrator, owner)
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE)
    role = models.ForeignKey(PersonCatalogueRelationRole, on_delete=CASCADE)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.catalogue)
