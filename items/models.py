from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

import uuid

from transcriptions.models import Transcription
from persons.models import Place, Person


class Language(models.Model):
    """
    A written language
    """

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


class Collection(models.Model):
    """
    The collection a catalogue belongs to
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=128, unique=True)

    def __str__(self):
        return self.name


class CollectionYear(models.Model):
    """
    The recorded year of a collection
    """
    year = models.IntegerField(_("Year"))
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.collection, self.year)


class CatalogueType(models.Model):
    """
    The type of a catalogue
    """
    name = models.CharField(_("Name of the catalogue type"), max_length=128, null=True)

    def __str__(self):
        return self.name


class Library(models.Model):
    """
    Library or institute that may hold one or more catalogues
    """
    name = models.CharField(_("The name of the library/institute"), max_length=128)

    def __str__(self):
        return self.name


class Catalogue(models.Model):
    """
    The catalogue an item occurs in
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
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

    def __str__(self):
        return "{0} ({1})".format(self.short_title, self.uuid)

class CatalogueHeldBy(models.Model):
    """
    A library/institute where a catalogue is held 
    """
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)

    def __str__(self):
        return _("{} held by {}").format(self.catalogue, self.library)


class BookFormat(models.Model):
    """
    A book format
    """

    name = models.CharField(_("Format name"), max_length=128, null=True)

    def __str__(self):
        return self.name


class BindingMaterialDetails(models.Model):
    """
    Binding material details
    """

    text = models.CharField(_("Binding material details text"), max_length=128, null=True)

    def __str__(self):
        return self.text


class Lot(models.Model):
    """
    Catalogue lot
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE, null=True)
    bookseller_category_books = models.TextField(_("Heading / category used to describe books"))
    bookseller_category_non_books = models.TextField(_("Heading / category for other, non-book items"))
    number_in_catalogue = models.CharField(_("Number of items as listed in catalogue"), max_length=128)
    item_as_listed_in_catalogue = models.TextField(_("Full item description, exactly as in the catalogue"))

    def __str__(self):
        return self.item_as_listed_in_catalogue


class Subject(models.Model):
    """
    Subject class
    """
    name = models.CharField(_("The text of the class"), max_length=128)

    def __str__(self):
        return self.name


class Work(models.Model):
    """
    A title of a work
    """

    title = models.TextField(_("Title of a work"))
    viaf_id = models.CharField(_("VIAF ID of a work"), max_length=32)

    def __str__(self):
        return self.title


class WorkSubject(models.Model):
    """
    Work-subject relation
    """
    work = models.ForeignKey(Work, on_delete=CASCADE)
    subject = models.ForeignKey(Subject, on_delete=CASCADE)

    def __str__(self):
        return "{}: {}".format(self.work, self.subject)


class WorkAuthor(models.Model):
    """
    Author of a work
    """
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

    collection = models.ForeignKey(Collection, on_delete=CASCADE)
    lot = models.ForeignKey(Lot, on_delete=CASCADE, null=True)
    number_of_volumes = models.CharField(_("Number of volumes, as listed in the catalogue"), max_length=128)
    sales_price = models.CharField(_("Sales price"), max_length=128)
    book_format = models.ForeignKey(BookFormat, on_delete=CASCADE)
    binding_material_details = models.ForeignKey(BindingMaterialDetails, on_delete=CASCADE)
    language = models.ForeignKey(Language, on_delete=CASCADE)
    work = models.ForeignKey(Work, on_delete=CASCADE)
    buyer = models.TextField(_("Buyer of an item"))  #TODO Could this also be a list/ENUM/controlled vocabulary?

    def __str__(self):
        return self.work.title

    def clean(self):
        if self.collection is not self.lot.catalogue.collection:
            raise ValidationError({'collection':
                _("The collection of this item and the collection of the catalogue of this item, are not the same.")
                                   })


class Publication(models.Model):
    """
    The publication information for an item
    """
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="publications")
    year = models.DateField(_("Year of publication"))
    year_tag = models.CharField(_("Year of publication tag"), max_length=128)
    place = models.ForeignKey(Place, on_delete=models.PROTECT)

    def __str__(self):
        return _("{}, published in {} in {}").format(self.item.work.title, self.year, self.place.name)


class Publisher(models.Model):
    """
    Publisher of an item
    """
    publisher = models.ForeignKey(Person, on_delete=CASCADE)
    publication = models.ForeignKey(Publication, on_delete=CASCADE)

    class Meta:
        unique_together = (("publisher", "publication"),)

    def __str__(self):
        return _("{} published {}").format(self.publisher, self.publication)


class YearInterval(models.Model):
    """
    An interval: start year - end year
    """
    start_year = models.IntegerField(_("Start year of interval"), null=False)
    end_year = models.IntegerField(_("End year of inter"), null=False)


class ItemYearIntervalRelation(models.Model):
    """
    A item - year interval relation
    """
    item = models.ForeignKey(Item, on_delete=CASCADE)
    year_interval = models.ForeignKey(YearInterval, on_delete=CASCADE)

    class Meta:
        unique_together = (("item", "year_interval"),)  # Multiple identical relation would be redundant


class PersonCollectionRelation(models.Model):
    """
    A person-collection relation (i.e. collector)
    """
    person = models.ForeignKey(Person, on_delete=CASCADE)
    collection = models.ForeignKey(Collection, on_delete=CASCADE)

    class Meta:
        unique_together = (("person", "collection"),)  # Multiple identical relation would be redundant

    def __str__(self):
        return _("{} is collector of {}").format(self.person, self.collection)


class PersonItemRelationRole(models.Model):
    """
    A role for a person-item relation
    """
    name = models.CharField(_("Role name for a person-item relation"), max_length=128, null=True)

    def __str__(self):
        return self.name


class PersonItemRelation(models.Model):
    """
    A person-item relation (e.g. author, translator, illustrator, owner)
    Note that the publisher relation is handled by the Publication/Publisher models.
    """

    person = models.ForeignKey(Person, on_delete=CASCADE)
    item = models.ForeignKey(Item, on_delete=CASCADE)
    role = models.ForeignKey(PersonItemRelationRole, on_delete=CASCADE)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.item)


class PersonCatalogueRelationRole(models.Model):
    """
    A type for a person-catalogue relation
    """
    name = models.CharField(_("Role name for a person-catalogue relation"), max_length=128)

    def __str__(self):
        return self.name


class PersonCatalogueRelation(models.Model):
    """
    A person-catalogue item relation (e.g. author, translator, illustrator, owner)
    """

    person = models.ForeignKey(Person, on_delete=CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE)
    role = models.ForeignKey(PersonCatalogueRelationRole, on_delete=CASCADE)

    def __str__(self):
        return _("{} is {} of {}").format(self.person, self.role, self.catalogue)
