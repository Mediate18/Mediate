from django.test import TestCase
from django.test import Client
from mediate.tools_testing import GenericCRUDTestMixin

from .models import *
from persons.tests import *
from transcriptions.models import *


# View tests #


class DatasetTests(GenericCRUDTestMixin, TestCase):
    """
    This is more or less a dummy test class since Dataset does not have any CRUD view (yet).
    """
    model = Dataset

    def get_add_form_data(self):
        return {
            'name': 'name_test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name_test2'
        }

    def test_List(self):
        # No Dataset list/table view exists
        pass

    def test_Detail(self):
        # No Dataset detail view exists
        pass

    def test_Delete(self):
        # No Dataset delete view exists
        pass

    def test_Add(self):
        # No Dataset add view exists
        pass

    def test_Change(self):
        # No Dataset change view exists
        pass


class Collection_TMPTests(GenericCRUDTestMixin, TestCase):
    model = Collection_TMP

    def get_add_form_data(self):
        dataset, created = Dataset.objects.get_or_create(**DatasetTests().get_add_form_data())
        return {
            'name': 'name_test',
            'dataset_id': dataset.pk
        }

    def get_change_form_data(self):
        return {
            'name': 'name_test2'
        }


class CollectionTests(GenericCRUDTestMixin, TestCase):
    model = Collection

    def get_add_form_data(self):
        source_material, created = SourceMaterial.objects.get_or_create(name="source_material test")
        transcription, created = Transcription.objects.get_or_create(source_material=source_material, curator="curator test")
        collection_tmp, created = Collection_TMP.objects.get_or_create(**Collection_TMPTests().get_add_form_data())
        return {
            'transcription_id': transcription.pk,
            'short_title': 'short_title test1',
            'full_title': 'full_title test',
            'preface_and_paratexts': 'preface_and_paratexts test',
            'year_of_publication': 1666,
            'bibliography': 'bibliography test',
            'collection_tmp_id': collection_tmp.pk
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
        When a Collection is deleted, all linked Editions that are not also linked to another Collection
        should be deleted
        :return:
        """

        # Create two Collections
        collection_data = self.get_add_form_data()
        collection1, created = self.model.objects.get_or_create(**collection_data)
        collection_data['short_title'] = 'short_title test2'
        collection2, created = self.model.objects.get_or_create(**collection_data)

        # Create two Lots
        lot1 = Lot.objects.create(collection=collection1, number_in_collection=1, index_in_collection=1,
                                  lot_as_listed_in_collection="lot1_text")
        lot2 = Lot.objects.create(collection=collection2, number_in_collection=1, index_in_collection=1,
                                  lot_as_listed_in_collection="lot2_text")

        # Create two Edition
        from items.models import Item, Edition
        edition1 = Edition.objects.create(year_start=1111)
        edition2 = Edition.objects.create(year_start=2222)

        # Create three Items. The third makes Edition2 link to two different Collections
        item1 = Item.objects.create(short_title="item1", lot=lot1, edition=edition1, index_in_lot=1)
        item2 = Item.objects.create(short_title="item2", lot=lot2, edition=edition2, index_in_lot=1)
        item3 = Item.objects.create(short_title="item3", lot=lot1, edition=edition2, index_in_lot=2)

        # Deleting collection1 should result in deleting edition1, but not edition2
        collection1.delete()

        def object_exists_in_database(obj):
            return obj.__class__.objects.filter(uuid=obj.pk).exists() if obj.pk else False

        self.assertFalse(object_exists_in_database(edition1))
        self.assertTrue(object_exists_in_database(edition2))


class Collection_TMPYearTests(GenericCRUDTestMixin, TestCase):
    model = Collection_TMPYear

    def get_add_form_data(self):
        collection_tmp, created = Collection_TMP.objects.get_or_create(**Collection_TMPTests().get_add_form_data())
        return {
            'year': 1666,
            'collection_tmp': collection_tmp
        }

    def get_change_form_data(self):
        return {
            'year': 1678,
        }

    def test_Detail(self):
        pass


class CollectionTypeTests(GenericCRUDTestMixin, TestCase):
    model = CollectionType

    def get_add_form_data(self):
        return {
            'name': 'name_test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name_test2'
        }

    def test_Detail(self):
        """TODO: add CollectionType detail template"""
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


class CollectionCollectionTypeRelationTests(GenericCRUDTestMixin, TestCase):
    model = CollectionCollectionTypeRelation

    def get_add_form_data(self):
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        collection_type, created = CollectionType.objects.get_or_create(**CollectionTypeTests().get_add_form_data())
        return {
            'collection_id': collection.pk,
            'type_id': collection_type.pk
        }

    def get_change_form_data(self):
        collection_change, created = Collection.objects.get_or_create(**CollectionTests().get_change_form_data())
        collection_type_change, created = CollectionType.objects.get_or_create(**CollectionTypeTests().get_change_form_data())
        return {
            'collection_id': collection_change.pk,
            'type_id': collection_type_change.pk
        }

    def test_Detail(self):
        """TODO: add CollectionCollectionTypeRelation detail template"""
        pass


class CollectionHeldByTests(GenericCRUDTestMixin, TestCase):
    model = CollectionHeldBy

    def get_add_form_data(self):
        library, created = Library.objects.get_or_create(**LibraryTests().get_add_form_data())
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        return {
            'library': library,
            'collection': collection
        }

    def get_change_form_data(self):
        library_change, created = Library.objects.get_or_create(**LibraryTests().get_change_form_data())
        collection_change, created = Collection.objects.get_or_create(**CollectionTests().get_change_form_data())

        return {
            'library': library_change,
            'collection': collection_change
        }

    def test_Detail(self):
        """TODO: add CollectionHeldBy detail template"""
        pass


class LotTests(GenericCRUDTestMixin, TestCase):
    model = Lot

    def get_add_form_data(self):
        category, created = Category.objects.get_or_create(**CategoryTests().get_add_form_data())
        collection = category.collection
        return {
            'collection_id': collection.pk,  # TODO: find out why the '_id' and '.pk' are necessary
            'number_in_collection': 1,
            'page_in_collection': 1,
            'sales_price': '10 gulden',
            'lot_as_listed_in_collection': 'lot_as_listed_in_collection test',
            'index_in_collection': 1,
            'category_id': category.pk
        }

    def get_change_form_data(self):
        return {
            'number_in_collection': 2
        }


class PersonCollection_TMPRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonCollection_TMPRelation

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        collection_tmp, created = Collection_TMP.objects.get_or_create(**Collection_TMPTests().get_add_form_data())
        return {
            'person_id': person.pk,
            'collection_tmp_id': collection_tmp.pk
        }

    def get_change_form_data(self):
        person_data = {**PersonTests().get_add_form_data(), **PersonTests().get_change_form_data()}
        person, created = Person.objects.get_or_create(**person_data)
        return {
            'person_id': person.pk
        }

    def test_Detail(self):
        """TODO: add a PersonCollection_TMPRelation detail template"""
        pass


class PersonCollectionRelationRoleTests(GenericCRUDTestMixin, TestCase):
    model = PersonCollectionRelationRole

    def get_add_form_data(self):
        return {
            'name': 'name test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }

    def test_Detail(self):
        """TODO: add a PersonCollectionRelationRole detail template"""
        pass


class PersonCollectionRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonCollectionRelation

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        role, created = PersonCollectionRelationRole.objects.get_or_create(**PersonCollectionRelationRoleTests().get_add_form_data())
        return {
            'person_id': person.pk,
            'collection_id': collection.pk,
            'role_id': role.pk
        }

    def get_change_form_data(self):
        person_data = {**PersonTests().get_add_form_data(), **PersonTests().get_change_form_data()}
        person, created = Person.objects.get_or_create(**person_data)
        return {
            'person_id': person.pk
        }

    def test_Detail(self):
        """TODO: add a PersonCollectionRelation detail template"""
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
        collection, created = Collection.objects.get_or_create(**CollectionTests().get_add_form_data())
        parent, created = Category.objects.get_or_create(collection=collection,
                                                         bookseller_category='bookseller_category test2')
        parisian_category, create = ParisianCategory.objects.get_or_create(**ParisianCategoryTests().get_add_form_data())
        return {
            'collection_id': collection.pk,
            'parent_id': parent.pk,
            'bookseller_category': 'bookseller_category test',
            'parisian_category_id': parisian_category.pk
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
    def test_collection_of_lot_and_category(self):
        """
        Test whether a exception is raised if the collection of a lot is not the same as
        the collection of the category of that lot.
        """
        with self.assertRaises(Exception) as exception_context_manager:
            # Create a dummy collection
            dummy_collection = Collection(short_title="short_title test")
            dummy_collection.save()

            # Create a second dummy collection
            dummy_collection2 = Collection(short_title="short_title test2")
            dummy_collection2.save()

            # Create a dummy category
            dummy_category = Category(collection=dummy_collection, bookseller_category="bookseller_category test")
            dummy_category.save()

            # Create a dummy lot
            dummy_lot = Lot(
                collection=dummy_collection2,
                number_in_collection=1,
                lot_as_listed_in_collection="lot_as_listed_in_collection test",
                category=dummy_category
            )

            dummy_lot.save()

        exception = exception_context_manager.exception

        self.assertEqual(exception.args, ("Lot {}: the collection is not the same as the category's collection"
                                         .format(dummy_lot),))

