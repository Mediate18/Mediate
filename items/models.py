from django.db import models
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.translation import ugettext_lazy as _

import uuid


class Place(models.Model):
    """
    A geographical place
    """

    name = models.CharField(_("Name of the place"), max_length=128, null=True)
    # type = models.ForeignKey(PlaceType)

    def __str__(self):
        return self.name


class Collection(models.Model):
    """
    The collection a catalogue belongs to
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name of the source"), max_length=128, unique=True)
    description = models.TextField(_("Description of the source"))
    place = models.ForeignKey(Place, on_delete=SET_NULL, null=True)

    def __str__(self):
        return self.name


class CatalogueType(models.Model):
    """
    The type of a catalogue
    """
    name = models.CharField(_("Name of the catalogue type"), max_length=128, null=True)

    def __str__(self):
        return self.name


class CatalogueSource(models.Model):
    """
    A catalogue source
    """
    name = models.CharField(_("Name of the source"), max_length=128, unique=True)
    description = models.TextField(_("Description of the source"))

    def __str__(self):
        return self.name


class Catalogue(models.Model):
    """
    The catalogue an item occurs in
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    source = models.ForeignKey(CatalogueSource, on_delete=SET_NULL, null=True)
    short_title = models.CharField(_("Short title"), max_length=128, null=True)
    full_title = models.TextField(_("Full title"), null=True)
    preface_and_paratexts = models.TextField(_("Preface or prefatory / concluding text"), null=True)
    type = models.ForeignKey(CatalogueType, on_delete=CASCADE, null=True)
    year_of_publication = models.IntegerField(_("Year of publication"), null=True)
    terminus_post_quem = models.IntegerField(_("Terminus post quem"), null=True)
    notes = models.TextField(_("Notes for the Mediate project"), null=True)
    bibliography = models.TextField(_("Bibliography"), null=True)
    collection = models.ForeignKey(Collection, on_delete=SET_NULL, null=True)

    def __str__(self):
        return "{0} ({1})".format(self.short_title, self.uuid)


class Publisher(models.Model):
    """
    A publisher of an item
    """
    name = models.CharField(_("Publisher name"), max_length=128, null=True)

    def __str__(self):
        return self.name


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


class Language(models.Model):
    """
    A written language, used for translations in written languages.
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


class Person(models.Model):
    """
    A person
    """

    name = models.CharField(_("Name"), max_length=128, null=True)
    viaf_id = models.CharField(_("VIAF ID (https://viaf.org)"), max_length=128, null=True)

    def __str__(self):
        return self.name


class PersonItemRelationRole(models.Model):
    """
    A role for a person-item relation
    """
    name = models.CharField(_("Role name for a person-item relation"), max_length=128, null=True)

    def __str__(self):
        return self.name


class CatalogueEntry(models.Model):
    """
    Catalogue Entry
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE, null=True)
    bookseller_category_books = models.TextField(_("Heading / category used to describe books"))
    bookseller_category_non_books = models.TextField(_("Heading / category for other, non-book items"))
    number_in_catalogue = models.CharField(_("Number of items as listed in catalogue"), max_length=128)
    item_as_listed_in_catalogue = models.TextField(_("Full item description, exactly as in the catalogue"))

    def __str__(self):
        return self.item_as_listed_in_catalogue


class TitleWork(models.Model):
    """
    A title of a work
    """

    text = models.TextField(_("Text of the title of a work"))

    def __str__(self):
        return self.text


class Item(models.Model):
    """
    Item
    """

    catalogue_entry = models.ForeignKey(CatalogueEntry, on_delete=CASCADE)
    place_of_publication = models.ForeignKey(Place, on_delete=CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=CASCADE)
    date_of_publication = models.DateField(_("Date of publication"))
    date_of_publication_tag = models.CharField(_("Date of publication tag"), max_length=128)
    number_of_volumes = models.CharField(_("Number of volumes, as listed in the catalogue"), max_length=128)
    sales_price = models.CharField(_("Sales price"), max_length=128)
    book_format = models.ForeignKey(BookFormat, on_delete=CASCADE)
    binding_material_details = models.ForeignKey(BindingMaterialDetails, on_delete=CASCADE)
    language = models.ForeignKey(Language, on_delete=CASCADE)
    title_work = models.ForeignKey(TitleWork, on_delete=CASCADE)
    buyer = models.TextField(_("Buyer of an item"))  #TODO Could this also be a list/ENUM/controlled vocabulary?

    def __str__(self):
        return self.title_work.text


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


class PersonItemRelation(models.Model):
    """
    A person-item relation (e.g. author, translator, illustrator, owner)
    """

    person = models.ForeignKey(Person, on_delete=CASCADE)
    item = models.ForeignKey(Item, on_delete=CASCADE)
    role = models.ForeignKey(PersonItemRelationRole, on_delete=CASCADE)


class PersonCatalogueRelationRole(models.Model):
    """
    A type for a person-catalogue relation
    """
    name = models.CharField(_("Type of person-catalogue relation"), max_length=128)

    def __str__(self):
        return self.name


class PersonCatalogueRelation(models.Model):
    """
    A person-catalogue item relation (e.g. author, translator, illustrator, owner)
    """

    person = models.ForeignKey(Person, on_delete=CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE)
    type = models.ForeignKey(PersonCatalogueRelationRole, on_delete=CASCADE)


# EQUIVALENTS
# Some objects of some classes may have equivalents defined due to spelling differences etc.
# The are defined in the file Masterfile place names etc. for automated extraction.xlsx
# The following class may be used to incorporate this data in this webapplication.
# An alternative would be to use Django's Generic Relations, so that there is one list of
# equivalents for multiple classes.

class PlaceEquivalent(models.Model):
    """
    Place name equivalent, e.g. due to different spelling and/or language
    """

    place = models.ForeignKey(Place, on_delete=CASCADE)
    text = models.CharField(_("Equivalent text"), max_length=128)


class PublisherEquivalent(models.Model):
    """
    Publisher name equivalent, e.g. due to different spelling and/or language
    """

    publisher = models.ForeignKey(Publisher, on_delete=CASCADE)
    text = models.CharField(_("Equivalent text"), max_length=128)


class BookFormatEquivalent(models.Model):
    """
    Book format name equivalent, e.g. due to different spelling and/or language
    """

    book_format = models.ForeignKey(BookFormat, on_delete=CASCADE)
    text = models.CharField(_("Equivalent text"), max_length=128)


class BindingMaterialDetailsEquivalent(models.Model):
    """
    Book format name equivalent, e.g. due to different spelling and/or language
    """

    binding_material_details = models.ForeignKey(BindingMaterialDetails, on_delete=CASCADE)
    text = models.CharField(_("Equivalent text"), max_length=128)


# UNUSED
# These classes are not used (yet).

class PlaceType(models.Model):
    """
    The type of a geographical place (e.g. city, state, country)
    """

    name = models.CharField(_("Name of the place type"), max_length=128)
