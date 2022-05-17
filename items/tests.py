from django.test import TestCase
from django.test import Client
from mediate.tools_testing import GenericCRUDTestMixin
from catalogues.tests import LotTests
from persons.tests import PersonTests

from .models import *


class LanguageTests(GenericCRUDTestMixin, TestCase):
    model = Language

    def get_add_form_data(self):
        return {
            'name': 'name test',
            'language_code_2char': 'xy',
            'language_code_3char': 'xyz',
            'description': 'description test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }


class BookFormatTests(GenericCRUDTestMixin, TestCase):
    model = BookFormat

    def get_add_form_data(self):
        return {
            'name': 'name test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class MaterialDetailsTests(GenericCRUDTestMixin, TestCase):
    model = MaterialDetails
    url_names = {'list': 'materialdetails'}

    def get_add_form_data(self):
        return {
            'description': 'description test'
        }

    def get_change_form_data(self):
        return {
            'description': 'description test2'
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class SubjectTests(GenericCRUDTestMixin, TestCase):
    model = Subject

    def get_add_form_data(self):
        return {
            'name': 'name test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class WorkTests(GenericCRUDTestMixin, TestCase):
    model = Work

    def get_add_form_data(self):
        return {
            'title': 'title test',
            'viaf_id': 'viaf_id test'
        }

    def get_change_form_data(self):
        return {
            'title': 'title test2',
            'viaf_id': 'viaf_id test2'
        }

    def test_Detail(self):
        """TODO: add a WorkSubject detail template"""
        pass


class WorkSubjectTests(GenericCRUDTestMixin, TestCase):
    model = WorkSubject

    def get_add_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_add_form_data())
        subject, created = Subject.objects.get_or_create(**SubjectTests().get_add_form_data())
        return {
            'work_id': work.pk,
            'subject_id': subject.pk
        }

    def get_change_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_change_form_data())
        return {
            'work_id': work.pk
        }

    def test_Detail(self):
        """TODO: a detail template"""
        pass


class WorkAuthorTests(GenericCRUDTestMixin, TestCase):
    model = WorkAuthor

    def get_add_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_add_form_data())
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        return {
            'work_id': work.pk,
            'author_id': person.pk
        }

    def get_change_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_change_form_data())
        return {
            'work_id': work.pk
        }

    def test_Detail(self):
        """TODO: a detail template"""
        pass


class ItemTests(GenericCRUDTestMixin, TestCase):
    model = Item

    @staticmethod
    def get_add_form_data():
        lot, created = Lot.objects.get_or_create(**LotTests().get_add_form_data())
        collection = lot.catalogue.collection
        book_format, created = BookFormat.objects.get_or_create(**BookFormatTests().get_add_form_data())
        edition, created = Edition.objects\
            .get_or_create(**EditionTests().get_add_form_data())
        return {
            'short_title': 'short_title',
            'lot_id':  lot.pk,
            'collection_id': collection.pk,
            'number_of_volumes': 'number_of_volumes test',
            'book_format_id': book_format.pk,
            'index_in_lot': 1,
            'edition_id': edition.pk
        }

    def get_change_form_data(self):
        return {
            'short_title': 'short_title2'
        }


class ItemTypeTests(GenericCRUDTestMixin, TestCase):
    model = ItemType

    def get_add_form_data(self):
        return {
            'name': 'name test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemItemTypeRelationTests(GenericCRUDTestMixin, TestCase):
    model = ItemItemTypeRelation

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        item_type, created = ItemType.objects.get_or_create(**ItemTypeTests().get_add_form_data())
        return {
            'item_id': item.pk,
            'type_id': item_type.pk
        }

    def get_change_form_data(self):
        item_type, created = ItemType.objects.get_or_create(**ItemTypeTests().get_change_form_data())
        return {
            'type_id': item_type.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemAuthorTests(GenericCRUDTestMixin, TestCase):
    model = ItemAuthor

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        return {
            'item_id': item.pk,
            'author_id': person.pk
        }

    def get_change_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        return {
            'author_id': person.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemLanguageRelationTests(GenericCRUDTestMixin, TestCase):
    model = ItemLanguageRelation

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        language, created = Language.objects.get_or_create(**LanguageTests().get_add_form_data())
        return {
            'item_id': item.pk,
            'language_id': language.pk
        }

    def get_change_form_data(self):
        language = Language.objects.all()[0]
        return {
            'language_id': language.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemWorkRelationTests(GenericCRUDTestMixin, TestCase):
    model = ItemWorkRelation

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        work, created = Work.objects.get_or_create(**WorkTests().get_add_form_data())
        return {
            'item_id': item.pk,
            'work_id': work.pk
        }

    def get_change_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_change_form_data())
        return {
            'work_id': work.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemMaterialDetailsRelationTests(GenericCRUDTestMixin, TestCase):
    model = ItemMaterialDetailsRelation

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        material_details, created = MaterialDetails.objects\
            .get_or_create(**MaterialDetailsTests().get_add_form_data())
        return {
            'item_id': item.pk,
            'material_details_id': material_details.pk
        }

    def get_change_form_data(self):
        material_details, created = MaterialDetails.objects \
            .get_or_create(**MaterialDetailsTests().get_add_form_data())
        return {
            'material_details_id': material_details.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class EditionTests(GenericCRUDTestMixin, TestCase):
    model = Edition

    def get_add_form_data(self):
        place, created = Place.objects.get_or_create(name="name test")
        return {
            'year_start': 1678,
            'year_tag': 'year_tag test',
            'terminus_post_quem': False,
            'place_id': place.pk,
            'url': 'url test'
        }

    def get_change_form_data(self):
        return {
            'year_tag': 'year_tag test2'
        }

    def test_Change(self):
        """Tests the Change view"""
        # Test permission
        permission = self.get_permission_string('change')
        self.assertTrue(self.user.has_perm(permission))

        # Get the Change form
        item_obj, created = Item.objects.get_or_create(**ItemTests.get_add_form_data())
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())
        item_obj.edition = obj
        item_obj.save()

        client = Client()
        client.login(username=self.username, password=self.password)

        # Note that the Edition update form is redirected to the item form (which is in fact
        # a combined Item and Manifestation form
        response = client.get(reverse_lazy(self.get_url_name('change'), args=[obj.uuid]))
        self.assertEqual(response.status_code, 302)
        redirect_url = response.url

        # Post to the Change form
        form_data = {**ItemTests.get_add_form_data(), **self.get_change_form_data()}
        response = client.post(redirect_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)


class PublisherTests(GenericCRUDTestMixin, TestCase):
    model = Publisher

    def get_add_form_data(self):
        publisher, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        edition, created = Edition.objects\
            .get_or_create(**EditionTests().get_add_form_data())
        return {
            'publisher_id': publisher.pk,
            'edition_id': edition.pk
        }

    def get_change_form_data(self):
        person_create_data = {**PersonTests().get_add_form_data(), ** PersonTests().get_change_form_data()}
        publisher, created = Person.objects.get_or_create(**person_create_data)
        return {
            'publisher_id': publisher.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class PersonItemRelationRoleTests(GenericCRUDTestMixin, TestCase):
    model = PersonItemRelationRole

    def get_add_form_data(self):
        return {
            'name': 'name test'
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2'
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class PersonItemRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonItemRelation

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        role, created = PersonItemRelationRole.objects\
            .get_or_create(**PersonItemRelationRoleTests().get_add_form_data())
        return {
            'person_id': person.pk,
            'item_id': item.pk,
            'role_id': role.pk
        }

    def get_change_form_data(self):
        role, created = PersonItemRelationRole.objects\
            .get_or_create(**PersonItemRelationRoleTests().get_change_form_data())
        return {
            'role_id': role.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass

