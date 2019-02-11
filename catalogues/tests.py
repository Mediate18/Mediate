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
        collection = Collection.objects.first()
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
    list_url_name = 'libraries'

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
        """TODO: add CatalogueHeldByTests detail template"""
        pass
