from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils import timezone
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APITestCase

from todolist.core.models import User
from todolist.goals.models import Goal, GoalCategory


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


class TestCategoryRetrieveView(APITestCase):
    def test_auth_required(self):
        response = self.client.get(reverse('retrieve-update-destroy-category', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        ('not exists', False),
        ('is deleted', True)
    ])
    def test_category_not_found(self, _, is_deleted):
        user = User.objects.create(username='test_user', password=make_password('test_password'))
        category = GoalCategory.objects.create(title='new_cat', user=user, is_deleted=is_deleted)

        self.client.force_login(user=user)
        response = self.client.get(reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk + 1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @parameterized.expand([
        ('owner', False),
        ('not_owner', True)
    ])
    def test_success(self, _, is_owner):
        owner = User.objects.create(username='owner', password=make_password('test_password'))
        not_owner = User.objects.create(username='not_owner', password=make_password('test_password'))
        category = GoalCategory.objects.create(title='new_cat', user=owner, is_deleted=False)

        self.client.force_login(user=owner if is_owner else not_owner)
        response = self.client.get(reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                'id': category.id,
                'user': {
                    'id': owner.id,
                    'username': owner.username,
                    'first_name': owner.first_name,
                    'last_name': owner.last_name,
                    'email': owner.email
                },
                'created': timezone.localtime(category.created).isoformat(),
                'updated': timezone.localtime(category.updated).isoformat(),
                'title': category.title
            }
        )


class TestUpdateCategory(APITestCase):

    def test_not_owner(self):
        category = GoalCategory.objects.create(
            title='new_cat',
            user=User.objects.create(username='test_user_1', password=make_password('test_password')),
            is_deleted=False
        )

        user = User.objects.create(username='test_user_2', password=make_password('test_password'))

        self.client.force_login(user=user)
        response = self.client.patch(reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        user = User.objects.create(username='test_user', password=make_password('test_password'))
        category = GoalCategory.objects.create(title='new_cat', user=user, is_deleted=False)

        self.client.force_login(user=user)
        response = self.client.patch(
            path=reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk}),
            data={'title': 'new_category'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db(fields=('title',))
        self.assertEqual(category.title, 'new_category')


class TestDeleteCategory(APITestCase):
    def test_not_owner(self):
        category = GoalCategory.objects.create(
            title='new_cat',
            user=User.objects.create(username='test_user_1', password=make_password('test_password')),
            is_deleted=False
        )

        user = User.objects.create(username='test_user_2', password=make_password('test_password'))

        self.client.force_login(user=user)
        response = self.client.delete(reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success_without_goals(self):
        user = User.objects.create(username='test_user', password=make_password('test_password'))
        category = GoalCategory.objects.create(title='new_cat', user=user, is_deleted=False)

        self.client.force_login(user=user)
        response = self.client.delete(reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        category.refresh_from_db(fields=('is_deleted',))
        self.assertTrue(category.is_deleted)

    def test_success_with_goals(self):
        user = User.objects.create(username='test_user', password=make_password('test_password'))
        category = GoalCategory.objects.create(title='new_cat', user=user, is_deleted=False)
        goal = Goal.objects.create(title='goal', category=category, due_date=timezone.now(), user=user)

        self.client.force_login(user=user)
        response = self.client.delete(reverse('retrieve-update-destroy-category', kwargs={'pk': category.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        category.refresh_from_db(fields=('is_deleted',))
        goal.refresh_from_db(fields=('status', ))
        self.assertEqual(goal.status, Goal.Status.archived)
