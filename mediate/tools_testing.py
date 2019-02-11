from django.contrib.auth.models import User, Group
from django.test import Client
from django.urls import reverse_lazy


class GenericCRUDTestMixin:
    """
    Tests for the obj model
    """

    def setUp(self):
        # For the purpose of printing queries in tearDown
        # from django.conf import settings
        # settings.DEBUG = True

        # a new test user is created for use during the tests
        self.username = 'test-user'
        self.email = 'example@example.com'
        self.password = 'test-user'
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.user.save()

        # Make the user member of the group dataset managers
        sandbox_group = Group.objects.get(name='sandbox')
        sandbox_group.user_set.add(self.user)

        # Take list_url_name from Meta or construct by appending 's'
        self.list_url_name = hasattr(self, 'list_url_name') and self.list_url_name \
                             or self.model.__name__.lower() + 's'

    def tearDown(self):
        # Printing queries
        # from django.db import connection
        # print("Queries: {}".format(connection.queries))
        pass

    def test_List(self):
        """Tests the List view"""
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.list_url_name))
        self.assertEqual(response.status_code, 200)

    def test_Add(self):
        """Tests the Create view"""
        # Get the Add form
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy('add_' + self.model.__name__.lower()))
        self.assertEqual(response.status_code, 200)

        # Post to the Add form
        response = client.post(reverse_lazy('add_' + self.model.__name__.lower()),
                               self.get_add_form_data(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_Detail(self):
        """Tests the Detail view"""
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())

        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.model.__name__.lower() +'_detail',
                                           args=[obj.uuid]))
        self.assertEqual(response.status_code, 200)

    def test_Change(self):
        """Tests the Change view"""
        # Get the Change form
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())

        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy('change_' + self.model.__name__.lower(),
                                           args=[obj.uuid]))
        self.assertEqual(response.status_code, 200)

        # Post to the Change form
        response = client.post(reverse_lazy('change_' + self.model.__name__.lower(),
                                            args=[obj.uuid]),
                               self.get_change_form_data(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_Delete(self):
        """Tests the Delete view"""
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())

        # Post to the Delete form
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.post(reverse_lazy('delete_' + self.model.__name__.lower(),
                                            args=[obj.uuid]), {}, follow=True)
        self.assertEqual(response.status_code, 200)
