from django.db import models
from django.dispatch import receiver
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericRelation

from computedfields.models import ComputedFieldsModel, computed, precomputed
from simple_history.models import HistoricalRecords

import uuid

from persons.models import Place, Person
from catalogues.models import Catalogue, Lot, ParisianCategory
from tagme.models import TaggedEntity

from simplemoderation.tools import moderated


class Language(models.Model):
    """
    A written language
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    language_code_2char = models.CharField(max_length=7, unique=True, null=True, blank=True, help_text=_(
        """Language code (2 characters long) of a written language. This also includes codes of the form zh-Hans, cf. IETF BCP 47"""))
    language_code_3char = models.CharField(max_length=3, unique=True, null=True, blank=True, help_text=_(
        """ISO 639-3 language code (3 characters long) of a written language."""))
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BookFormat(models.Model):
    """
    A book format
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Format name"), max_length=128, null=True)

    def __str__(self):
        return self.name


class MaterialDetails(models.Model):
    """
    Material details
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(_("Binding material details description"), max_length=128, null=True)

    def __str__(self):
        return self.description


class Subject(models.Model):
    """
    Subject class
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("The text of the class"), max_length=128)

    def __str__(self):
        return self.name


class Work(models.Model):
    """
    A title of a work
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(_("Title of a work"))
    viaf_id = models.CharField(_("VIAF ID of a work"), max_length=128, null=True, blank=True, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class WorkSubject(models.Model):
    """
    Work-subject relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work = models.ForeignKey(Work, on_delete=CASCADE)
    subject = models.ForeignKey(Subject, on_delete=CASCADE)

    def __str__(self):
        return "{}: {}".format(self.work, self.subject)


class WorkAuthor(models.Model):
    """
    Author of a work
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work = models.ForeignKey(Work, on_delete=CASCADE, related_name="authors")
    author = models.ForeignKey(Person, on_delete=CASCADE, related_name="works")

    class Meta:
        unique_together = (("work", "author"),)

    def __str__(self):
        return _("{} wrote {}").format(self.author, self.work)


@moderated()
class Item(ComputedFieldsModel):
    """
    Item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    lot = models.ForeignKey(Lot, on_delete=SET_NULL, null=True)
    catalogue = models.ForeignKey(Catalogue, on_delete=SET_NULL, null=True, blank=True)
    number_of_volumes = models.CharField(_("Number of volumes, as listed in the collection"),
                                         max_length=128, null=True, blank=True)
    book_format = models.ForeignKey(BookFormat, on_delete=SET_NULL, null=True, related_name='items', blank=True)
    index_in_lot = models.IntegerField(_("Index in the lot"))
    edition = models.ForeignKey('Edition', on_delete=models.PROTECT, related_name="items")  # See also the delete method
    non_book = models.BooleanField(default=False, editable=False)
    parisian_category = models.ForeignKey(ParisianCategory, on_delete=SET_NULL, null=True, blank=True)
    uncountable_book_items = models.BooleanField(default=False)

    tags = GenericRelation(TaggedEntity, related_query_name='items')

    history = HistoricalRecords(bases=[ComputedFieldsModel])

    @computed(models.IntegerField(null=True), depends=[('lot.collection', ['year_of_publication'])])
    def collection_year_of_publication(self):
        try:
            return self.lot.collection.year_of_publication
        except:
            return None

    @computed(models.CharField(max_length=128, null=True), depends=[('lot.collection', ['short_title'])])
    def collection_short_title(self):
        try:
            return self.lot.collection.short_title
        except:
            return None

    @computed(models.UUIDField(null=True), depends=[('lot.collection.catalogue.dataset', ['uuid'])])
    def dataset_uuid(self):
        try:
            return self.lot.collection.catalogue.first().dataset.uuid
        except:
            return None

    @computed(models.IntegerField(null=True))
    def lot_index_in_collection(self):
        try:
            return self.lot.index_in_collection
        except:
            return None

    @computed(models.CharField(max_length=128, null=True))
    def lot_lot_as_listed_in_collection(self):
        try:
            return self.lot.lot_as_listed_in_collection[:128]
        except:
            return None

    class Meta:
        indexes = [
            models.Index(fields=["collection_year_of_publication",
                                 "collection_short_title",
                                 "lot_index_in_collection",
                                 "index_in_lot",
                                 "lot_lot_as_listed_in_collection"]),
            models.Index(fields=["dataset_uuid"]),
            models.Index(fields=["non_book"])
        ]

    def __str__(self):
        return self.short_title

    def clean(self):
        if self.lot and self.lot.collection and self.lot.collection.catalogue:
            collection_catalogue = self.lot.collection.catalogue.first()
            if not self.catalogue:
                self.catalogue = collection_catalogue
            elif self.catalogue != collection_catalogue:
                raise ValidationError({'catalogue':
                    _("The catalogue of this item and the catalogue of the collection of this item, are not the same.")
                                   })

    def determine_non_book(self):
        original_non_book = self.non_book
        if ItemItemTypeRelation.objects.filter(item=self):
            if ItemItemTypeRelation.objects.filter(item=self).exclude(type__non_book=False):
                self.non_book = True
            else:
                self.non_book = False
        else:
            self.non_book = False

        # Return whether non_book is changed
        return not original_non_book == self.non_book

    @precomputed
    def save(self, *args, **kwargs):
        self.determine_non_book()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('item_detail', args=[str(self.uuid)])

    def delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

        # As long as Item.edition has on_delete=models.PROTECT,
        # the following will only succeed if this is the only Item of the Edition
        self.edition.delete()

    def get_other_items_in_lot(self):
        return Item.objects.prefetch_related('edition')\
            .filter(lot=self.lot).exclude(index_in_lot=self.index_in_lot).order_by('index_in_lot')


class ItemType(models.Model):
    """
    Item type
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the item type"), max_length=128, null=True)
    non_book = models.BooleanField(_("Is non book type"), default=True)

    def __str__(self):
        return self.name


class ItemItemTypeRelation(models.Model):
    """
    Relation between Item and Item Type
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=CASCADE)
    type = models.ForeignKey(ItemType, on_delete=CASCADE)

    class Meta:
        unique_together = (('item', 'type'),)


@receiver(models.signals.post_save, sender=ItemItemTypeRelation)
@receiver(models.signals.post_delete, sender=ItemItemTypeRelation)
def set_item_non_book(sender, instance, **kwargs):
    """
    Triggers and propagates the non-book check. 
    :param sender: 
    :param instance: 
    :param kwargs: 
    :return: 
    """
    item = instance.item
    changed = item.determine_non_book()
    if changed:
        item.save()


@receiver(models.signals.post_save, sender=ItemType)
@receiver(models.signals.post_delete, sender=ItemType)
def set_item_non_book_for_type(sender, instance, **kwargs):
    for item in Item.objects.filter(itemitemtyperelation__type=instance):
        changed = item.determine_non_book()
        if changed:
            item.save()


class ItemAuthor(models.Model):
    """
    Author of a work
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=CASCADE, related_name='authors')
    author = models.ForeignKey(Person, on_delete=CASCADE, related_name='items')

    class Meta:
        unique_together = (('item', 'author'),)

    def __str__(self):
        return _("{} wrote item {}").format(self.author, self.item)


class ItemLanguageRelation(models.Model):
    """
    The language of an item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=CASCADE, related_name='languages')
    language = models.ForeignKey(Language, on_delete=CASCADE, related_name='items')

    class Meta:
        unique_together = (('item', 'language'),)

    def __str__(self):
        return _("{} is written in {}").format(self.item, self.language)


class ItemWorkRelation(models.Model):
    """
    An item containing a work
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=CASCADE, related_name='works')
    work = models.ForeignKey(Work, on_delete=CASCADE, related_name='items')

    class Meta:
        unique_together = (('item', 'work'),)

    def __str__(self):
        return _("{} contains {}").format(self.item, self.work)


class ItemMaterialDetailsRelation(models.Model):
    """
    An item containing a work
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=CASCADE)
    material_details = models.ForeignKey(MaterialDetails, on_delete=CASCADE, related_name='items')

    class Meta:
        unique_together = (('item', 'material_details'),)

    def __str__(self):
        return _("{} contains {}").format(self.item, self.material_details)


class Edition(models.Model):
    """
    The edition information for an item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year_start = models.IntegerField(_("Year of publication - start"), null=True, blank=True)
    year_end = models.IntegerField(_("Year of publication - end"), null=True, blank=True)
    year_tag = models.CharField(_("Year of publication tag"), max_length=128, blank=True)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.CharField(_("URL"), max_length=1024, blank=True)

    def __str__(self):
        str_elements = []
        if self.place:
            str_elements.append("{}".format(self.place.name))
        publishers = [publisher.publisher.short_name for publisher in Publisher.objects.filter(edition=self)
                      if publisher.publisher.short_name]
        if publishers:
            str_elements += publishers
        year_range_str = self.get_year_range_str()
        if year_range_str:
            str_elements.append(year_range_str)
        published_str = ", ".join(str_elements)if str_elements else _("Empty edition").format()
        return published_str

    def get_year_range_str(self):
        year_range_str = "{}".format(self.year_start) if self.year_start else ""
        year_range_str += " - {}".format(self.year_end) if self.year_end else ""
        return year_range_str

    def clean(self):
        if self.year_start is None and self.year_end is not None:
            raise ValidationError(
                _('Year of publication - start may not be empty if Year of publication - end is non-empty MODEL'),
                code='model__empty_year_start_non_emtpy_year_end',
            )

    def get_absolute_url(self):
        return reverse_lazy('edition_detail', args=[str(self.uuid)])


class Publisher(models.Model):
    """
    Publisher of an item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publisher = models.ForeignKey(Person, on_delete=CASCADE)
    edition = models.ForeignKey(Edition, on_delete=CASCADE)

    class Meta:
        unique_together = (("publisher", "edition"),)

    def __str__(self):
        return _("{} published {}").format(self.publisher, self.edition)


class PublicationPlace(models.Model):
    """
    Place of publication
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edition = models.ForeignKey(Edition, on_delete=CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("edition", "place"),)

    def __str__(self):
        return _("{} is published in {}").format(self.edition, self.place)


class PersonItemRelationRole(models.Model):
    """
    A role for a person-item relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Role name for a person-item relation"), max_length=128, null=True)

    def __str__(self):
        return self.name


@moderated()
class PersonItemRelation(models.Model):
    """
    A person-item relation (e.g. author, translator, illustrator, owner)
    Note that the publisher relation is handled by the Edition/Publisher models.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    item = models.ForeignKey(Item, on_delete=CASCADE)
    role = models.ForeignKey(PersonItemRelationRole, on_delete=CASCADE)
    notes = models.TextField(_("Notes"), null=True, blank=True)

    class Meta:
        unique_together = (("person", "item", "role"),)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.item)

    def get_absolute_url(self):
        return reverse_lazy('change_personitemrelation', args=[str(self.uuid)])


# Enable the simple-history registration:
from .history import *


# Clear cache when a model object is saved
from django.db.models.signals import post_save, post_delete
from mediate.tools import receiver_with_multiple_senders
from django.core.cache import cache


@receiver_with_multiple_senders([post_save, post_delete],[
    Language, BookFormat, MaterialDetails, Subject, Work, WorkSubject, WorkAuthor, Item, ItemType, ItemItemTypeRelation,
    ItemAuthor, ItemLanguageRelation, ItemWorkRelation, ItemMaterialDetailsRelation, Edition, Publisher,
    PersonItemRelationRole, PersonItemRelation
])
def clear_cache(sender, instance, **kwargs):
    cache.clear()