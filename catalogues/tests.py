from django.test import TestCase
from django.test import Client
from mediate.tools_testing import GenericCRUDTestMixin

from .models import *
from persons.tests import *
from transcriptions.models import *


# View tests #


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
        source_material, created = SourceMaterial.objects.get_or_create(name="source_material test")
        transcription, created = Transcription.objects.get_or_create(source_material=source_material, curator="curator test")
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

    def test_List(self):
        """Tests the List view"""
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.get_url_name('list')))
        self.assertEqual(response.status_code, 200)

    def test_Deletion_of_Editions(self):
        """
        When a Catalogue is deleted, all linked Editions that are not also linked to another Catalogue
        should be deleted
        :return:
        """

        # Create two Catalogues
        catalogue_data = self.get_add_form_data()
        catalogue1, created = self.model.objects.get_or_create(**catalogue_data)
        catalogue_data['short_title'] = 'short_title test2'
        catalogue2, created = self.model.objects.get_or_create(**catalogue_data)

        # Create two Lots
        lot1 = Lot.objects.create(catalogue=catalogue1, number_in_catalogue=1, lot_as_listed_in_catalogue="lot1_text")
        lot2 = Lot.objects.create(catalogue=catalogue2, number_in_catalogue=1, lot_as_listed_in_catalogue="lot2_text")

        # Create two Edition
        from items.models import Item, Edition
        edition1 = Edition.objects.create(year_start=1111)
        edition2 = Edition.objects.create(year_start=2222)

        # Create three Items. The third makes Edition2 link to two different Catalogues
        item1 = Item.objects.create(short_title="item1", lot=lot1, edition=edition1, index_in_lot=1)
        item2 = Item.objects.create(short_title="item2", lot=lot2, edition=edition2, index_in_lot=1)
        item3 = Item.objects.create(short_title="item3", lot=lot1, edition=edition2, index_in_lot=2)

        # Deleting catalogue1 should result in deleting edition1, but not edition2
        catalogue1.delete()

        def object_exists_in_database(obj):
            return obj.__class__.objects.filter(uuid=obj.pk).exists() if obj.pk else False

        self.assertFalse(object_exists_in_database(edition1))
        self.assertTrue(object_exists_in_database(edition2))


class CollectionYearTests(GenericCRUDTestMixin, TestCase):
    model = CollectionYear

    def get_add_form_data(self):
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
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
        category, created = Category.objects.get_or_create(**CategoryTests().get_add_form_data())
        catalogue = category.catalogue
        return {
            'catalogue_id': catalogue.pk,  # TODO: find out why the '_id' and '.pk' are necessary
            'number_in_catalogue': 1,
            'page_in_catalogue': 1,
            'sales_price': '10 gulden',
            'lot_as_listed_in_catalogue': 'lot_as_listed_in_catalogue test',
            'index_in_catalogue': 1,
            'category_id': category.pk
        }

    def get_change_form_data(self):
        return {
            'number_in_catalogue': 2
        }


class PersonCollectionRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonCollectionRelation

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        return {
            'person': person,
            'collection': collection
        }

    def get_change_form_data(self):
        person_data = {**PersonTests().get_add_form_data(), **PersonTests().get_change_form_data()}
        person, created = Person.objects.get_or_create(person_data)
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
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        catalogue, created = Catalogue.objects.get_or_create(**CatalogueTests().get_add_form_data())
        role, created = PersonCatalogueRelationRole.objects.get_or_create(**PersonCatalogueRelationRoleTests().get_add_form_data())
        return {
            'person': person,
            'catalogue': catalogue,
            'role': role
        }

    def get_change_form_data(self):
        person_data = {**PersonTests().get_add_form_data(), **PersonTests().get_change_form_data()}
        person, created = Person.objects.get_or_create(person_data)
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
        catalogue, created = Catalogue.objects.get_or_create(**CatalogueTests().get_add_form_data())
        parent, created = Category.objects.get_or_create(catalogue=catalogue,
                                                         bookseller_category='bookseller_category test2')
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


# Model tests #


class LotModelTests(TestCase):
    def test_catalogue_of_lot_and_category(self):
        """
        Test whether a exception is raised if the catalogue of a lot is not the same as
        the catalogue of the category of that lot.
        """
        with self.assertRaises(Exception) as exception_context_manager:
            # Create a dummy catalogue
            dummy_catalogue = Catalogue(short_title="short_title test")
            dummy_catalogue.save()

            # Create a second dummy catalogue
            dummy_catalogue2 = Catalogue(short_title="short_title test2")
            dummy_catalogue2.save()

            # Create a dummy category
            dummy_category = Category(catalogue=dummy_catalogue, bookseller_category="bookseller_category test")
            dummy_category.save()

            # Create a dummy lot
            dummy_lot = Lot(
                catalogue=dummy_catalogue2,
                number_in_catalogue=1,
                lot_as_listed_in_catalogue="lot_as_listed_in_catalogue test",
                category=dummy_category
            )

            dummy_lot.save()

        exception = exception_context_manager.exception

        self.assertEqual(exception.args, ("Lot {}: the catalogue is not the as the category's catalogue"
                                         .format(dummy_lot),))

