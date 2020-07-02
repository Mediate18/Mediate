from django.db import models
from django.db.models import ProtectedError
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericRelation

import uuid

from persons.models import Person, Place
from transcriptions.models import Transcription
from tagme.models import TaggedEntity
from simplemoderation.tools import moderated


class Collection(models.Model):
    """
    The collection a catalogue belongs to
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('collection_detail', args=[str(self.uuid)])


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


@moderated(['short_title', 'notes'])
class Catalogue(models.Model):
    """
    The catalogue an item occurs in
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transcription = models.ForeignKey(Transcription, on_delete=SET_NULL, null=True)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    full_title = models.TextField(_("Full title"), null=True)
    preface_and_paratexts = models.TextField(_("Preface or prefatory / concluding text"), null=True)
    year_of_publication = models.IntegerField(_("Year of publication"), null=True)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    notes = models.TextField(_("Notes for the Mediate project"), null=True)
    bibliography = models.TextField(_("Bibliography"), null=True)
    collection = models.ForeignKey(Collection, on_delete=SET_NULL, null=True)

    tags = GenericRelation(TaggedEntity, related_query_name='catalogues')

    class Meta:
        ordering = ['year_of_publication', 'short_title']

    def __str__(self):
        return "{0}".format(self.short_title)

    def get_absolute_url(self):
        return reverse_lazy('catalogue_detail', args=[str(self.uuid)])

    def delete(self, *args, **kwargs):
        # Gather edition IDs that are linked to this catalogue
        from items.models import Edition  # To prevent an import error (probably circular imports)
        editions = list(Edition.objects.filter(items__lot__catalogue=self).values_list('uuid', flat=True))

        # Delete the catalogue
        super().delete(*args, **kwargs)

        # Delete the linked editions
        for id in editions:
            try:
                edition = Edition.objects.get(uuid=id)
                edition.delete()
            except ProtectedError:
                # No problem, this is suppost to happen due to the on_delete=PROTECT in the Item-Edition relation
                pass

    def item_count(self):
        from items.models import Item
        return Item.objects.filter(lot__catalogue=self).count()

    @property
    def sorted_lot_set(self):
        return self.lot_set.order_by('index_in_catalogue')


class CatalogueCatalogueTypeRelation(models.Model):
    """
    A catalogue-catalogue type relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)
    type = models.ForeignKey(CatalogueType, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("catalogue", "type"),)  # Multiple identical relations would be redundant


class CatalogueHeldBy(models.Model):
    """
    A library/institute where a catalogue is held 
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)

    def __str__(self):
        return _("{} held by {}").format(self.catalogue, self.library)


@moderated(['lot_as_listed_in_catalogue'])
class Lot(models.Model):
    """
    Catalogue lot
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE, null=True)
    number_in_catalogue = models.CharField(_("Number in catalogue"), max_length=128)
    page_in_catalogue = models.IntegerField(_("Page in catalogue"), null=True, blank=True)
    sales_price = models.CharField(_("Sales price"), max_length=128, blank=True)
    lot_as_listed_in_catalogue = models.TextField(_("Full lot description, exactly as in the catalogue"))
    index_in_catalogue = models.IntegerField(_("Index in catalogue"), null=True)
    category = models.ForeignKey('Category', on_delete=SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.lot_as_listed_in_catalogue

    def save(self, *args, **kwargs):
        # Check whether the catalogue of the category is the same catalogue
        if not self.category or self.catalogue == self.category.catalogue:
            super(Lot, self).save(*args, **kwargs)
        else:
            raise Exception(_("Lot {}: the catalogue is not the same as the category's catalogue").format(self))

    def get_absolute_url(self):
        return reverse_lazy('lot_detail', args=[str(self.uuid)])

    def get_previous_lots(self, number=4):
        index_in_catalogue = self.index_in_catalogue
        index_start = index_in_catalogue - number
        index_end = index_in_catalogue - 1
        return Lot.objects.filter(catalogue=self.catalogue, index_in_catalogue__gte=index_start,
                                  index_in_catalogue__lte=index_end)


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


class CataloguePlaceRelationType(models.Model):
    """
    Type of relation between a catalogue and a place
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class CataloguePlaceRelation(models.Model):
    """
    Publication place for catalogues 
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=CASCADE, related_name='related_catalogues')
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE, related_name='related_places')
    type = models.ForeignKey(CataloguePlaceRelationType, on_delete=SET_NULL, null=True)

    def __str__(self):
        return _("{} is published in {}").format(self.catalogue, self.place)


class ParisianCategory(models.Model):
    """
    A category from Parisian system of 17th century booksellers.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name_plural = "parisian categories"

    def __str__(self):
        return "{} ({})".format(self.name, self.description)


class Category(models.Model):
    """
    A category as found in a catalogue.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=SET_NULL, null=True)
    parent = models.ForeignKey('self', on_delete=SET_NULL, null=True)
    bookseller_category = models.TextField(_("Heading / category used to describe books"))
    parisian_category = models.ForeignKey(ParisianCategory, on_delete=SET_NULL, null=True)

    class Meta:
        ordering = ['bookseller_category']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.bookseller_category

    def get_absolute_url(self):
        return reverse_lazy('category_detail', args=[str(self.uuid)])

    def save(self, *args, **kwargs):
        # Check whether the catalogue of the parent is the same catalogue
        if not self.parent or self.catalogue == self.parent.catalogue:
            super(Category, self).save(*args, **kwargs)
        else:
            raise Exception(_("Category {}: the catalogue is not the as the parent's catalogue").format(self))


# Enable the simple-history registration:
from .history import *
