from django.test import TestCase, Client
from mediate.tools_testing import GenericCRUDTestMixin

from .models import *


class PlaceTests(GenericCRUDTestMixin, TestCase):
    model = Place

    def get_add_form_data(self):
        return {
            'name': 'name test',
            'cerl_id': 'cnl00016323'  # Nijmegen
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2',
            'cerl_id': 'cnl00015951'  # Utrecht
        }


class ReligionTests(GenericCRUDTestMixin, TestCase):
    model = Religion

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
        """TODO: add detail template"""
        pass


class PersonTests(GenericCRUDTestMixin, TestCase):
    model = Person

    def get_add_form_data(self):
        place, created = Place.objects.get_or_create(**PlaceTests().get_add_form_data())
        return {
            'short_name': 'short_name test',
            'surname': 'surname test',
            'first_names': 'first_names test',
            'date_of_birth': '1678',
            'date_of_death': '1765',
            'sex': 'FEMALE',
            'city_of_birth_id': place.pk,
            'city_of_death_id': place.pk
        }

    def get_change_form_data(self):
        place, created = Place.objects.get_or_create(**PlaceTests().get_change_form_data())
        return {
            'short_name': 'short_name test2',
            'surname': 'surname test2',
            'first_names': 'first_names test2',
            'date_of_birth': '1600',
            'date_of_death': '1700',
            'sex': 'MALE',
            'city_of_birth_id': place.pk,
            'city_of_death_id': place.pk
        }

    def test_Add(self):
        """Tests the Create view"""
        # Test permission
        permission = self.get_permission_string('add')
        self.assertTrue(self.user.has_perm(permission))

        # Get the Add form
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.get_url_name('add')))
        self.assertEqual(response.status_code, 200)

        # Post to the Add form
        add_form_data = self.get_add_form_data().update({
            # FormSet form data
            "alternative_names-TOTAL_FORMS": 0,
            "alternative_names-INITIAL_FORMS": 0,
            "alternative_names-MIN_NUM_FORMS": 0,
            "alternative_names-MAX_NUM_FORMS": 0,

            "residence_set-TOTAL_FORMS": 0,
            "residence_set-INITIAL_FORMS": 0,
            "residence_set-MIN_NUM_FORMS": 0,
            "residence_set-MAX_NUM_FORMS": 0,

            "relations_when_first-TOTAL_FORMS": 0,
            "relations_when_first-INITIAL_FORMS": 0,
            "relations_when_first-MIN_NUM_FORMS": 0,
            "relations_when_first-MAX_NUM_FORMS": 0,

            "relations_when_second-TOTAL_FORMS": 0,
            "relations_when_second-INITIAL_FORMS": 0,
            "relations_when_second-MIN_NUM_FORMS": 0,
            "relations_when_second-MAX_NUM_FORMS": 0,
        })
        response = client.post(reverse_lazy(self.get_url_name('add')),
                               add_form_data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_Change(self):
        """Tests the Change view"""
        # Test permission
        permission = self.get_permission_string('change')
        self.assertTrue(self.user.has_perm(permission))

        # Get the Change form
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())

        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.get_url_name('change'), args=[obj.uuid]))
        self.assertEqual(response.status_code, 200)

        # Post to the Change form
        change_form_data = self.get_change_form_data().update({
            # FormSet form data
            "alternative_names-TOTAL_FORMS": 0,
            "alternative_names-INITIAL_FORMS": 0,
            "alternative_names-MIN_NUM_FORMS": 0,
            "alternative_names-MAX_NUM_FORMS": 0,

            "residence_set-TOTAL_FORMS": 0,
            "residence_set-INITIAL_FORMS": 0,
            "residence_set-MIN_NUM_FORMS": 0,
            "residence_set-MAX_NUM_FORMS": 0,

            "relations_when_first-TOTAL_FORMS": 0,
            "relations_when_first-INITIAL_FORMS": 0,
            "relations_when_first-MIN_NUM_FORMS": 0,
            "relations_when_first-MAX_NUM_FORMS": 0,

            "relations_when_second-TOTAL_FORMS": 0,
            "relations_when_second-INITIAL_FORMS": 0,
            "relations_when_second-MIN_NUM_FORMS": 0,
            "relations_when_second-MAX_NUM_FORMS": 0,
        })
        response = client.post(reverse_lazy(self.get_url_name('change'), args=[obj.uuid]),
                               change_form_data, follow=True)
        self.assertEqual(response.status_code, 200)


class ReligiousAffiliationTests(GenericCRUDTestMixin, TestCase):
    model = ReligiousAffiliation

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        religion, created = Religion.objects.get_or_create(**ReligionTests().get_add_form_data())
        return {
            'person_id': person.pk,
            'religion_id': religion.pk
        }

    def get_change_form_data(self):
        religion, created = Religion.objects.get_or_create(**ReligionTests().get_change_form_data())
        return {
            'religion_id': religion.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ResidenceTests(GenericCRUDTestMixin, TestCase):
    model = Residence

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        place, created = Place.objects.get_or_create(**PlaceTests().get_add_form_data())
        return {
            'person_id': person.pk,
            'place_id': place.pk,
            'start_year': 1678,
            'end_year': 1765
        }

    def get_change_form_data(self):
        return {
            'start_year': 1600,
            'end_year': 1700
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class ProfessionTests(GenericCRUDTestMixin, TestCase):
    model = Profession

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
        """TODO: add detail template"""
        pass


class PersonProfessionTests(GenericCRUDTestMixin, TestCase):
    model = PersonProfession

    def get_add_form_data(self):
        person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        profession, created = Profession.objects.get_or_create(**ProfessionTests().get_add_form_data())
        return {
            'person_id': person.pk,
            'profession_id': profession.pk
        }

    def get_change_form_data(self):
        profession, created = Profession.objects.get_or_create(**ProfessionTests().get_change_form_data())
        return {
            'profession_id': profession.pk
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class PersonPersonRelationTypeTests(GenericCRUDTestMixin, TestCase):
    model = PersonPersonRelationType

    def get_add_form_data(self):
        return {
            'name': 'name test',
            'directed': True
        }

    def get_change_form_data(self):
        return {
            'name': 'name test2',
            'directed': False
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass


class PersonPersonRelationTests(GenericCRUDTestMixin, TestCase):
    model = PersonPersonRelation

    def get_add_form_data(self):
        first_person, created = Person.objects.get_or_create(**PersonTests().get_add_form_data())
        second_person, created = Person.objects.get_or_create(**PersonTests().get_change_form_data())
        relation_type, created = PersonPersonRelationType.objects\
            .get_or_create(**PersonPersonRelationTypeTests().get_add_form_data())
        return {
            'first_person_id': first_person.pk,
            'second_person_id': second_person.pk,
            'type_id': relation_type.pk,
            'start_year': 1678,
            'end_year': 1765
        }

    def get_change_form_data(self):
        return {
            'start_year': 1600,
            'end_year': 1700
        }

    def test_Detail(self):
        """TODO: add detail template"""
        pass
