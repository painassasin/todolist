from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from todolist.core.models import User
from todolist.goals.models import GoalCategory


class TestCategoryCreateView(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='test_user', password=make_password('test_password'))
        self.url = reverse('create-category')

    def test_auth_required(self):
        response = self.client.post(self.url, {'title': 'new_category'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        self.client.force_login(user=self.user)
        response = self.client.post(self.url, {'title': 'new_category'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_cat: GoalCategory = GoalCategory.objects.last()
        self.assertEqual(new_cat.title, 'new_category')
        self.assertEqual(new_cat.user, self.user)
        self.assertFalse(new_cat.is_deleted)


class TestCategoryListView(APITestCase):

    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='test_user_1', password=make_password('test_password'))
        self.user_2 = User.objects.create(username='test_user_2', password=make_password('test_password'))
        self.user_1_cat = GoalCategory.objects.create(title='new_cat_1', user=self.user_1, is_deleted=False)
        self.user_1_deleted_cat = GoalCategory.objects.create(title='new_cat_2', user=self.user_1, is_deleted=True)
        self.user_2_cat = GoalCategory.objects.create(title='new_cat_3', user=self.user_2, is_deleted=False)

    def test_auth_required(self):
        response = self.client.get(reverse('list-categories'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        self.client.force_login(user=self.user_1)
        response = self.client.get(reverse('list-categories'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['id'], self.user_1_cat.id)
        self.assertDictEqual(response.json()[0]['user'], {
            'id': self.user_1.id,
            'username': self.user_1.username,
            'first_name': self.user_1.first_name,
            'last_name': self.user_1.last_name,
            'email': self.user_1.email,
        })
        self.assertEqual(response.json()[0]['title'], self.user_1_cat.title)
        self.assertFalse(response.json()[0]['is_deleted'])
