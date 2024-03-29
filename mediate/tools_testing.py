from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse_lazy

from guardian.shortcuts import assign_perm

from catalogues.models import Dataset


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

        # Add permission to change the test dataset
        dataset, created = Dataset.objects.get_or_create(name='name_test')
        assign_perm('catalogues.change_dataset', self.user, dataset)
        assign_perm('catalogues.view_dataset', self.user, dataset)


    def get_permission_string(self, verb):
        content_type = ContentType.objects.get_for_model(self.model)
        return content_type.app_label + "." + verb + "_" + self.model.__name__.lower()

    def get_url_name(self, verb, postfix=False):
        """Get either the specified url name or a constructed one"""
        if hasattr(self, 'url_names'):
            if verb in self.url_names:
                return self.url_names[verb]
        if verb == 'list':
            return self.model.__name__.lower() + 's'
        if postfix:
            return self.model.__name__.lower() + '_' + verb
        return verb + '_' + self.model.__name__.lower()

    def tearDown(self):
        # Printing queries
        # from django.db import connection
        # print("Queries: {}".format(connection.queries))
        self.user.delete()
        pass

    def test_List(self):
        """Tests the List view"""
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.get_url_name('list')))
        self.assertEqual(response.status_code, 200)

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
        response = client.post(reverse_lazy(self.get_url_name('add')),
                               self.get_add_form_data(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_Detail(self):
        """Tests the Detail view"""
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())

        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse_lazy(self.get_url_name('detail', postfix=True),
                                           args=[obj.uuid]))
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
        response = client.post(reverse_lazy(self.get_url_name('change'), args=[obj.uuid]),
                               self.get_change_form_data(), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_Delete(self):
        """Tests the Delete view"""
        obj, created = self.model.objects.get_or_create(**self.get_add_form_data())

        # Post to the Delete form
        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.post(reverse_lazy(self.get_url_name('delete'), args=[obj.uuid]), {},
                               HTTP_REFERER=reverse_lazy('dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
