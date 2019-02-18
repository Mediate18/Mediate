from django.test import TestCase
from mediate.tools_testing import GenericCRUDTestMixin

from .models import *


class LanguageTests(GenericCRUDTestMixin, TestCase):
    model = Language

    def get_add_form_data(self):
        return {
            'name': 'name test',
            'language_code_2char': 'xx',
            'language_code_3char': 'xxx',
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
            'subject': subject
        }

    def get_change_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_change_form_data())
        return {
            'work': work
        }

    def test_Detail(self):
        """TODO: a detail template"""
        pass


class WorkAuthorTests(GenericCRUDTestMixin, TestCase):
    model = WorkAuthor

    def get_add_form_data(self):
        work, created = Work.objects.get_or_create(**WorkTests().get_add_form_data())
        person = Person.objects.first()
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

    def get_add_form_data(self):
        lot = Lot.objects.first()
        collection = lot.catalogue.collection
        book_format = BookFormat.objects.first()
        manifestation, created = Manifestation.objects\
            .get_or_create(**ManifestationTests().get_add_form_data())
        return {
            'short_title': 'short_title',
            'lot':  lot,
            'collection': collection,
            'number_of_volumes': 'number_of_volumes test',
            'book_format': book_format,
            'index_in_lot': 1,
            'manifestation': manifestation
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
        type, created = ItemType.objects.get_or_create(**ItemTypeTests().get_add_form_data())
        return {
            'item_id': item.pk,
            'type': type
        }

    def get_change_form_data(self):
        type = ItemType.objects.get_or_create(**ItemTypeTests().get_change_form_data())
        return {
            'type': type
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemAuthorTests(GenericCRUDTestMixin, TestCase):
    model = ItemAuthor

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        person = Person.objects.first()
        return {
            'item_id': item.pk,
            'author': person
        }

    def get_change_form_data(self):
        person = Person.objects.all()[1]
        return {
            'person': person
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ItemLanguageRelationTests(GenericCRUDTestMixin, TestCase):
    model = ItemLanguageRelation

    def get_add_form_data(self):
        item, created = Item.objects.get_or_create(**ItemTests().get_add_form_data())
        language = Language.objects.first()
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
            'material_details': material_details
        }

    def get_change_form_data(self):
        material_details, created = MaterialDetails.objects \
            .get_or_create(**MaterialDetailsTests().get_add_form_data())
        return {
            'material_details': material_details
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ManifestationTests(GenericCRUDTestMixin, TestCase):
    model = Manifestation

    def get_add_form_data(self):
        place = Place.objects.first()
        return {
            'year': 1678,
            'year_tag': 'year_tag test',
            'terminus_post_quem': False,
            'place_id': place.pk,
            'url': 'url test'
        }

    def get_change_form_data(self):
        return {
            'year_tag': 'year_tag test2'
        }


class PublisherTests(GenericCRUDTestMixin, TestCase):
    model = Publisher

    def get_add_form_data(self):
        publisher = Person.objects.first()
        manifestation, created = Manifestation.objects\
            .get_or_create(**ManifestationTests().get_add_form_data())
        return {
            'publisher_id': publisher.pk,
            'manifestation_id': manifestation.pk
        }

    def get_change_form_data(self):
        publisher = Person.objects.all()[1]
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
        person = Person.objects.first()
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

