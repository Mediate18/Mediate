from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.contrib.contenttypes.fields import GenericRelation

import uuid

from persons.models import Place, Person
from catalogues.models import Collection, Lot
from tagme.models import TaggedEntity

from simplemoderation.tools import moderated


class Language(models.Model):
    """
    A written language
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    language_code_2char = models.CharField(max_length=7, unique=True, null=False, blank=False, help_text=_(
        """Language code (2 characters long) of a written language. This also includes codes of the form zh-Hans, cf. IETF BCP 47"""))
    language_code_3char = models.CharField(max_length=3, unique=True, null=False, blank=False, help_text=_(
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
class Item(models.Model):
    """
    Item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    lot = models.ForeignKey(Lot, on_delete=CASCADE, null=True)
    collection = models.ForeignKey(Collection, on_delete=CASCADE, null=True, blank=True)
    number_of_volumes = models.CharField(_("Number of volumes, as listed in the catalogue"),
                                         max_length=128, null=True, blank=True)
    book_format = models.ForeignKey(BookFormat, on_delete=SET_NULL, null=True, related_name='items', blank=True)
    index_in_lot = models.IntegerField(_("Index in the lot"))
    edition = models.ForeignKey('Edition', on_delete=models.PROTECT, related_name="items")

    tags = GenericRelation(TaggedEntity, related_query_name='items')

    class Meta:
        ordering = ['lot__catalogue__year_of_publication', 'lot__catalogue__short_title',
                    'lot__lot_as_listed_in_catalogue']

    def __str__(self):
        return self.short_title

    def clean(self):
        if self.lot and self.lot.catalogue and self.lot.catalogue.collection:
            if not self.collection:
                self.collection = self.lot.catalogue.collection
            elif self.collection != self.lot.catalogue.collection:
                raise ValidationError({'collection':
                    _("The collection of this item and the collection of the catalogue of this item, are not the same.")
                                   })

    def get_absolute_url(self):
        return reverse_lazy('item_detail', args=[str(self.uuid)])

    def delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)
        self.edition.delete()


class ItemType(models.Model):
    """
    Item type
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the item type"), max_length=128, null=True)

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
    year = models.IntegerField(_("Year of publication"), null=True, blank=True)
    year_tag = models.CharField(_("Year of publication tag"), max_length=128, blank=True)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    place = models.ForeignKey(Place, on_delete=models.PROTECT, null=True, blank=True)
    url = models.CharField(_("URL"), max_length=1024, blank=True)

    def __str__(self):
        str_elements = []
        if self.place:
            str_elements.append("{}".format(self.place.name))
        publishers = Publisher.objects.filter(edition=self)
        if publishers and publishers[0].publisher.short_name:
            str_elements.append(publishers[0].publisher.short_name)
        if self.year:
            str_elements.append("{}".format(self.year))
        published_str = ", ".join(str_elements)if str_elements else _("Empty edition").format()
        return published_str

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

    class Meta:
        unique_together = (("person", "item", "role"),)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.item)


# Enable the simple-history registration:
from .history import *
