from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _


class CatalogueType(models.Model):
    """
    The type of a catalogue
    """
    name = models.CharField(_("Name of the catalogue type"), max_length=128)


class Catalogue(models.Model):
    """
    The catalogue a book item occurs in
    """

    uuid = models.UUIDField()
    short_title = models.CharField(_("Short title"), max_length=128)
    full_title = models.TextField(_("Full title"))
    preface_and_paratexts = models.TextField(_("Preface or prefatory / concluding text"))
    type = models.ForeignKey(CatalogueType, on_delete=CASCADE)
    year_of_publication_start = models.IntegerField(_("Year of publication (start of interval)"))
    year_of_publication_end = models.IntegerField(_("Year of publication (end of interval)"))
    year_of_publication_text = models.CharField(_("Year of publication text"), max_length=128)
    notes = models.TextField(_("Notes for the Mediate project"))
    bibliography = models.TextField(_("Bibliography"))


class Place(models.Model):
    """
    A geographical place
    """

    name = models.CharField(_("Name of the place"), max_length=128)
    # type = models.ForeignKey(PlaceType)


class Publisher(models.Model):
    """
    A publisher of a book item
    """
    name = models.CharField(_("Publisher name"), max_length=128)


class BookFormat(models.Model):
    """
    A book format
    """

    name = models.CharField(_("Format name"), max_length=128)


class BindingMaterialDetails(models.Model):
    """
    Binding material details
    """

    text = models.CharField(_("Binding material details text"), max_length=128)


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

    name = models.CharField(_("Name"), max_length=128)
    viaf_id = models.CharField(_("VIAF ID (https://viaf.org)"), max_length=128)


class PersonBookItemRelationType(models.Model):
    """
    A type for a person-book item relation
    """
    name = models.CharField(_("Type of person-book item relation"), max_length=128)


class CatalogueItem(models.Model):
    """
    Catalogue item
    """

    uuid = models.UUIDField()
    bookseller_category_books = models.TextField(_("Heading / category used to describe books"))
    bookseller_category_non_books = models.TextField(_("Heading / category for other, non-book items"))
    number_in_catalogue = models.CharField(_("Number of items as listed in catalogue"), max_length=128)
    item_as_listed_in_catalogue = models.TextField(_("Full item description, exactly as in the catalogue"))


class TitleWork(models.Model):
    """
    A title of a work
    """

    text = models.TextField(_("Text of the title of a work"))


class BookItem(models.Model):
    """
    Book item
    """

    catalogue_item = models.ForeignKey(CatalogueItem, on_delete=CASCADE)
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
    buyer = models.TextField(_("Buyer of a book item"))  #TODO Could this also be a list/ENUM/controlled vocabulary?


class PersonBookItemRelation(models.Model):
    """
    A person-book item relation (e.g. author, translator, illustrator, owner)
    """

    person = models.ForeignKey(Person, on_delete=CASCADE)
    book_item = models.ForeignKey(BookItem, on_delete=CASCADE)
    type = models.ForeignKey(PersonBookItemRelationType, on_delete=CASCADE)


class PersonCatalogueRelationType(models.Model):
    """
    A type for a person-catalogue relation
    """
    name = models.CharField(_("Type of person-catalogue relation"), max_length=128)


class PersonCatalogueRelation(models.Model):
    """
    A person-catalogue item relation (e.g. author, translator, illustrator, owner)
    """

    person = models.ForeignKey(Person, on_delete=CASCADE)
    catalogue = models.ForeignKey(Catalogue, on_delete=CASCADE)
    type = models.ForeignKey(PersonCatalogueRelationType, on_delete=CASCADE)


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
