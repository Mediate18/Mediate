from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

import uuid

from persons.models import Place, Person
from catalogues.models import Collection, Lot


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
    viaf_id = models.CharField(_("VIAF ID of a work"), max_length=32, null=True, blank=True, unique=True)

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


class Item(models.Model):
    """
    Item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    lot = models.ForeignKey(Lot, on_delete=CASCADE, null=True)
    collection = models.ForeignKey(Collection, on_delete=CASCADE)
    number_of_volumes = models.CharField(_("Number of volumes, as listed in the catalogue"), max_length=128)

    def __str__(self):
        return self.short_title

    def clean(self):
        if self.collection != self.lot.catalogue.collection:
            raise ValidationError({'collection':
                _("The collection of this item and the collection of the catalogue of this item, are not the same.")
                                   })


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


class ItemBookFormatRelation(models.Model):
    """
    The book format of an item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=CASCADE, related_name='book_formats')
    book_format = models.ForeignKey(BookFormat, on_delete=CASCADE, related_name='items')

    class Meta:
        unique_together = (('item', 'book_format'),)

    def __str__(self):
        return _("Format of {}: {}").format(self.item, self.book_format)


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


class Publication(models.Model):
    """
    The publication information for an item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="publications")
    year = models.IntegerField(_("Year of publication"))
    year_tag = models.CharField(_("Year of publication tag"), max_length=128)
    terminus_post_quem = models.BooleanField(_("Terminus post quem"), default=False)
    place = models.ForeignKey(Place, on_delete=models.PROTECT)

    def __str__(self):
        return _("{}, published in {} in {}").format(self.item.work.title, self.year, self.place.name)


class Publisher(models.Model):
    """
    Publisher of an item
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publisher = models.ForeignKey(Person, on_delete=CASCADE)
    publication = models.ForeignKey(Publication, on_delete=CASCADE)

    class Meta:
        unique_together = (("publisher", "publication"),)

    def __str__(self):
        return _("{} published {}").format(self.publisher, self.publication)


class PersonItemRelationRole(models.Model):
    """
    A role for a person-item relation
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Role name for a person-item relation"), max_length=128, null=True)

    def __str__(self):
        return self.name


class PersonItemRelation(models.Model):
    """
    A person-item relation (e.g. author, translator, illustrator, owner)
    Note that the publisher relation is handled by the Publication/Publisher models.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=CASCADE)
    item = models.ForeignKey(Item, on_delete=CASCADE)
    role = models.ForeignKey(PersonItemRelationRole, on_delete=CASCADE)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.item)
