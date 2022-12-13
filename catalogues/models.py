from django.db import models, transaction
from django.db.models import ProtectedError, F
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericRelation
from django.dispatch import receiver
from django.core.exceptions import ValidationError


import uuid

from persons.models import Person, Place
from transcriptions.models import Transcription, ShelfMark
from tagme.models import TaggedEntity
from simplemoderation.tools import moderated


class Dataset(models.Model):
    """
    The dataset a catalogue belongs to
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)

    def __str__(self):
        return self.name



class Catalogue(models.Model):
    """
    The catalogue a collection belongs to
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.PROTECT)
    # full_title = models.TextField(_("Full title"), null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('catalogue_detail', args=[str(self.uuid)])

    def item_count(self):
        from items.models import Item
        item_count = Item.objects.filter(lot__collection__catalogue=self).count()
        uncountable_book_items = Item.objects.filter(lot__collection__catalogue=self, uncountable_book_items=True).count()
        return item_count + uncountable_book_items


class CatalogueYear(models.Model):
    """
    The recorded year of a catalogue
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField(_("Year"))
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.catalogue, self.year)


class CollectionType(models.Model):
    """
    The type of a collection
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the collection type"), max_length=128, null=True)

    def __str__(self):
        return self.name


class Library(models.Model):
    """
    Library or institute that may hold one or more collections
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("The name of the library/institute"), max_length=128)

    class Meta:
        verbose_name_plural = "libraries"

    def __str__(self):
        return self.name


@moderated(['short_title', 'notes'])
class Collection(models.Model):
    """
    The collection an item occurs in
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transcription = models.ForeignKey(Transcription, on_delete=SET_NULL, null=True)
    shelf_mark = models.ForeignKey(ShelfMark, on_delete=SET_NULL, null=True)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    full_title = models.TextField(_("Full title"), null=True)
    preface_and_paratexts = models.TextField(_("Preface or prefatory / concluding text"), null=True)
    year_of_publication = models.IntegerField(_("Year of publication"), null=True)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    notes = models.TextField(_("Notes for the Mediate project"), null=True)
    bibliography = models.TextField(_("Bibliography"), null=True)
    catalogue = models.ManyToManyField(Catalogue, related_name='collection', through='CatalogueCollectionRelation')

    tags = GenericRelation(TaggedEntity, related_query_name='collections')

    class Meta:
        ordering = ['year_of_publication', 'short_title']

    def __str__(self):
        return "{0}".format(self.short_title)

    def get_absolute_url(self):
        return reverse_lazy('collection_detail', args=[str(self.uuid)])

    def delete(self, *args, **kwargs):
        # Gather edition IDs that are linked to this collection
        from items.models import Edition  # To prevent an import error (probably circular imports)
        editions = list(Edition.objects.filter(items__lot__collection=self).values_list('uuid', flat=True))

        # Delete the collection
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
        item_count = Item.objects.filter(lot__collection=self).count()
        uncountable_book_items = Item.objects.filter(lot__collection=self, uncountable_book_items=True).count()
        return item_count + uncountable_book_items

    def has_uncountable_book_items(self):
        from items.models import Item
        return Item.objects.filter(lot__collection=self, uncountable_book_items=True).exists()

    @property
    def sorted_lot_set(self):
        return self.lot_set.order_by('index_in_collection', 'number_in_collection')


class CatalogueCollectionRelation(models.Model):
    """
    The Catalogue - Collection 'through' model
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE)
    collection = models.ForeignKey(Collection, on_delete=CASCADE)


def check_unique_dataset_for_catalogue_collection(catalogue, collection):
    """
    Checks whether all catalogues of a collection belong to a single dataset
    """
    first_catalogue_of_collection = collection.catalogue.first()
    if first_catalogue_of_collection and first_catalogue_of_collection.dataset != catalogue.dataset:
        raise ValidationError("All catalogues of one collection must belong to the same dataset")


@receiver(models.signals.m2m_changed, sender=Collection.catalogue.through)
def check_unique_dataset(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Checks whether all catalogues of a collection belong to a single dataset on adding a relation
    """
    # Is there at least one pk?
    first_pk = next(iter(pk_set)) if pk_set is not None and len(pk_set) else None
    if not first_pk:
        return

    if not 'pre_add':
        return

    catalogue  = instance if     reverse else model.objects.get(uuid=first_pk)
    collection = instance if not reverse else model.objects.get(uuid=first_pk)
    check_unique_dataset_for_catalogue_collection(catalogue, collection)


class CollectionCollectionTypeRelation(models.Model):
    """
    A collection-collection type relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    type = models.ForeignKey(CollectionType, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("collection", "type"),)  # Multiple identical relations would be redundant


class CollectionHeldBy(models.Model):
    """
    A library/institute where a collection is held
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return _("{} held by {}").format(self.collection, self.library)


@moderated(['lot_as_listed_in_collection'])
class Lot(models.Model):
    """
    Collection lot
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(Collection, on_delete=CASCADE, null=True)
    number_in_collection = models.CharField(_("Number in collection"), max_length=128)
    page_in_collection = models.IntegerField(_("Page in collection"), null=True, blank=True)
    sales_price = models.CharField(_("Sales price"), max_length=128, blank=True)
    lot_as_listed_in_collection = models.TextField(_("Full lot description, exactly as in the collection"))
    index_in_collection = models.IntegerField(_("Index in collection"), null=True)
    category = models.ForeignKey('Category', on_delete=SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.lot_as_listed_in_collection

    def save(self, *args, **kwargs):
        # Check whether the collection of the category is the same collection
        if not self.category or self.collection == self.category.collection:
            with transaction.atomic():
                # Add 1 to index_in_collection for all lots with index_in_collection greater than or equal to this index
                Lot.objects.filter(collection=self.collection, index_in_collection__gte=self.index_in_collection)\
                    .update(index_in_collection=F('index_in_collection') + 1)
                super(Lot, self).save(*args, **kwargs)
        else:
            raise Exception(_("Lot {}: the collection is not the same as the category's collection").format(self))


    def get_absolute_url(self):
        return reverse_lazy('lot_detail', args=[str(self.uuid)])

    def get_previous_lots(self, number=4):
        index_incollection = self.index_in_collection
        index_start = index_incollection - number
        index_end = index_incollection - 1
        return Lot.objects.filter(collection=self.collection, index_in_collection__gte=index_start,
                                  index_in_collection__lte=index_end)


class PersonCatalogueRelation(models.Model):
    """
    A person-catalogue relation (i.e. collector)
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE)

    class Meta:
        unique_together = (("person", "catalogue"),)  # Multiple identical relation would be redundant

    def __str__(self):
        return _("{} is collector of {}").format(self.person, self.catalogue)


class PersonCollectionRelationRole(models.Model):
    """
    A type for a person-collection relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Role name for a person-collection relation"), max_length=128)

    def __str__(self):
        return self.name


class PersonCollectionRelation(models.Model):
    """
    A person-collection item relation (e.g. author, translator, illustrator, owner)
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    collection = models.ForeignKey(Collection, on_delete=CASCADE)
    role = models.ForeignKey(PersonCollectionRelationRole, on_delete=CASCADE)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.collection)


class CollectionPlaceRelationType(models.Model):
    """
    Type of relation between a collection and a place
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class CollectionPlaceRelation(models.Model):
    """
    Publication place for collections
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=CASCADE, related_name='related_collections')
    collection = models.ForeignKey(Collection, on_delete=CASCADE, related_name='related_places')
    type = models.ForeignKey(CollectionPlaceRelationType, on_delete=SET_NULL, null=True)

    def __str__(self):
        return _("{} is published in {}").format(self.collection, self.place)


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
        return "{} ({})".format(self.name, self.description) if self.description else self.name


class Category(models.Model):
    """
    A category as found in a collection.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(Collection, on_delete=SET_NULL, null=True)
    parent = models.ForeignKey('self', on_delete=SET_NULL, null=True)
    bookseller_category = models.TextField(_("Heading / category used to describe books"))
    parisian_category = models.ForeignKey(ParisianCategory, on_delete=SET_NULL, null=True)

    class Meta:
        ordering = ['bookseller_category']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.bookseller_category if self.bookseller_category \
            else "Empty heading (Collection: {}, Parisian category: {})".format(self.collection, self.parisian_category if self.parisian_category else '-')

    def get_absolute_url(self):
        return reverse_lazy('category_detail', args=[str(self.uuid)])

    def save(self, *args, **kwargs):
        # Check whether the collection of the parent is the same collection
        if not self.parent or self.collection == self.parent.collection:
            super(Category, self).save(*args, **kwargs)
        else:
            raise Exception(_("Category {}: the collection is not the as the parent's collection").format(self))


# Enable the simple-history registration:
from .history import *


# Clear cache when a model object is saved
from django.db.models.signals import post_save, post_delete
from mediate.tools import receiver_with_multiple_senders
from django.core.cache import cache


@receiver_with_multiple_senders([post_save, post_delete],[
    Dataset, Catalogue, CatalogueYear, CollectionType, Library, Collection, CatalogueCollectionRelation,
    CollectionCollectionTypeRelation, CollectionHeldBy, Lot, PersonCatalogueRelation, PersonCollectionRelationRole,
    PersonCollectionRelation, CollectionPlaceRelationType, CollectionPlaceRelation, ParisianCategory, Category
])
def clear_cache(sender, instance, **kwargs):
    cache.clear()