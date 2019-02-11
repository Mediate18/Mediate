from django.test import TestCase
from mediate.tools_testing import GenericCRUDTestMixin

from .models import *
from transcriptions.models import *


class CollectionTests(GenericCRUDTestMixin, TestCase):
    model = Collection

    def get_add_form_data(self):
        return {
            'name': 'name_test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name_test2'
        }


class CatalogueTests(GenericCRUDTestMixin, TestCase):
    model = Catalogue

    def get_add_form_data(self):
        transcription = Transcription.objects.first()
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        return {
            'transcription': transcription,
            'short_title': 'short_title test1',
            'full_title': 'full_title test',
            'preface_and_paratexts': 'preface_and_paratexts test',
            'year_of_publication': 1666,
            'bibliography': 'bibliography test',
            'collection': collection
        }

    def get_change_form_data(self):
        return {
            'short_title': 'short_title_test2'
        }


class CollectionYearTests(GenericCRUDTestMixin, TestCase):
    model = CollectionYear

    def get_add_form_data(self):
        collection = Collection.objects.first()
        return {
            'year': 1666,
            'collection': collection
        }

    def get_change_form_data(self):
        return {
            'year': 1678,
        }

    def test_Detail(self):
        pass


class CatalogueTypeTests(GenericCRUDTestMixin, TestCase):
    model = CatalogueType

    def get_add_form_data(self):
        return {
            'name': 'name_test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name_test2'
        }

    def test_Detail(self):
        """TODO: add CatalogueType detail template"""
        pass


class LibraryTests(GenericCRUDTestMixin, TestCase):
    model = Library
    url_names = {'list': 'libraries'}

    def get_add_form_data(self):
        return {
            'name': 'name_test1'
        }

    def get_change_form_data(self):
        return {
            'name': 'name_test2'
        }

    def test_Detail(self):
        """TODO: add Library detail template"""
        pass


class CatalogueCatalogueTypeRelationTests(GenericCRUDTestMixin, TestCase):
    model = CatalogueCatalogueTypeRelation

    def get_add_form_data(self):
        catalogue, created = Catalogue.objects.get_or_create(**CatalogueTests().get_add_form_data())
        catalogue_type, created = CatalogueType.objects.get_or_create(**CatalogueTypeTests().get_add_form_data())
        return {
            'catalogue': catalogue,
            'type': catalogue_type
        }

    def get_change_form_data(self):
        catalogue_change, created = Catalogue.objects.get_or_create(**CatalogueTests().get_change_form_data())
        catalogue_type_change, created = CatalogueType.objects.get_or_create(**CatalogueTypeTests().get_change_form_data())
        return {
            'catalogue': catalogue_change,
            'type': catalogue_type_change
        }

    def test_Detail(self):
        """TODO: add CatalogueCatalogueTypeRelation detail template"""
        pass


class CatalogueHeldByTests(GenericCRUDTestMixin, TestCase):
    model = CatalogueHeldBy

    def get_add_form_data(self):
        library, created = Library.objects.get_or_create(**LibraryTests().get_add_form_data())
        catalogue, created = Catalogue.objects.get_or_create(**CatalogueTests().get_add_form_data())
        return {
            'library': library,
            'catalogue': catalogue
        }

    def get_change_form_data(self):
        library_change, created = Library.objects.get_or_create(**LibraryTests().get_change_form_data())
        catalogue_change, created = Catalogue.objects.get_or_create(**CatalogueTests().get_change_form_data())

        return {
            'library': library_change,
            'catalogue': catalogue_change
        }

    def test_Detail(self):
        """TODO: add CatalogueHeldBy detail template"""
        pass


class LotTests(GenericCRUDTestMixin, TestCase):
    model = Lot

    def get_add_form_data(self):
        category = Category.objects.first()
        catalogue = category.catalogue
        return {
            'catalogue_id': catalogue.pk,  # TODO: find out why the '_id' and '.pk' are necessary
            'number_in_catalogue': 1,
            'page_in_catalogue': 1,
            'sales_price': '10 gulden',
            'lot_as_listed_in_catalogue': 'lot_as_listed_in_catalogue test',
            'index_in_catalogue': 1,
            'category': category
        }

    def get_change_form_data(self):
        return {
            'number_in_catalogue': 2
        }


class PersonCollectionRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonCollectionRelation

    def get_add_form_data(self):
        person = Person.objects.first()
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        return {
            'person': person,
            'collection': collection
        }

    def get_change_form_data(self):
        person = Person.objects.all()[1]
        return {
            'person': person
        }

    def test_Detail(self):
        """TODO: add a PersonCollectionRelation detail template"""
        pass


class PersonCatalogueRelationRoleTests(GenericCRUDTestMixin, TestCase):
    model = PersonCatalogueRelationRole

    def get_add_form_data(self):
        return {
            'name': 'name test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }

    def test_Detail(self):
        """TODO: add a PersonCatalogueRelationRole detail template"""
        pass


class PersonCatalogueRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonCatalogueRelation

    def get_add_form_data(self):
        person = Person.objects.first()
        catalogue, created = Catalogue.objects.get_or_create(**CatalogueTests().get_add_form_data())
        role, created = PersonCatalogueRelationRole.objects.get_or_create(**PersonCatalogueRelationRoleTests().get_add_form_data())
        return {
            'person': person,
            'catalogue': catalogue,
            'role': role
        }

    def get_change_form_data(self):
        person = Person.objects.all()[1]
        return {
            'person': person
        }

    def test_Detail(self):
        """TODO: add a PersonCatalogueRelation detail template"""
        pass


class ParisianCategoryTests(GenericCRUDTestMixin, TestCase):
    model = ParisianCategory
    url_names = {'list': 'parisiancategories'}

    def get_add_form_data(self):
        return {
            'name': 'name test',
            'description': 'description test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2',
            'description': 'description test2'
        }

    def test_Detail(self):
        """TODO: add a ParisianCategory detail template"""
        pass


class CategoryTests(GenericCRUDTestMixin, TestCase):
    model = Category
    url_names = {'list': 'categories'}

    def get_add_form_data(self):
        parent = Category.objects.first()
        catalogue = parent.catalogue
        parisian_category, create = ParisianCategory.objects.get_or_create(**ParisianCategoryTests().get_add_form_data())
        return {
            'catalogue': catalogue,
            'parent': parent,
            'bookseller_category': 'bookseller_category test',
            'parisian_category': parisian_category
        }

    def get_change_form_data(self):
        return {
            'bookseller_category': 'bookseller_category test2'
        }

    def test_Detail(self):
        """TODO: add a ParisianCategory detail template"""
        pass


