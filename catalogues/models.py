from django.db import models, transaction
from django.db.models import ProtectedError, F
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericRelation


import uuid

from persons.models import Person, Place
from transcriptions.models import Transcription
from tagme.models import TaggedEntity
from simplemoderation.tools import moderated


class Dataset(models.Model):
    """
    The dataset a collection_tmp belongs to
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)

    def __str__(self):
        return self.name



class Collection_TMP(models.Model):
    """
    The collection_tmp a collection belongs to
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('collection_tmp_detail', args=[str(self.uuid)])


class Collection_TMPYear(models.Model):
    """
    The recorded year of a collection_tmp
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField(_("Year"))
    collection_tmp = models.ForeignKey(Collection_TMP, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.collection_tmp, self.year)


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
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    full_title = models.TextField(_("Full title"), null=True)
    preface_and_paratexts = models.TextField(_("Preface or prefatory / concluding text"), null=True)
    year_of_publication = models.IntegerField(_("Year of publication"), null=True)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    notes = models.TextField(_("Notes for the Mediate project"), null=True)
    bibliography = models.TextField(_("Bibliography"), null=True)
    collection_tmp = models.ForeignKey(Collection_TMP, on_delete=SET_NULL, null=True)

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
        return Item.objects.filter(lot__collection=self).count()

    @property
    def sorted_lot_set(self):
        return self.lot_set.order_by('index_in_collection', 'number_in_collection')


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


class PersonCollection_TMPRelation(models.Model):
    """
    A person-collection_tmp relation (i.e. collector)
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    collection_tmp = models.ForeignKey(Collection_TMP, on_delete=CASCADE)

    class Meta:
        unique_together = (("person", "collection_tmp"),)  # Multiple identical relation would be redundant

    def __str__(self):
        return _("{} is collector of {}").format(self.person, self.collection_tmp)


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
