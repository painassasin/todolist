from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from todolist.core.models import User
from todolist.goals.models import Goal, GoalCategory


class TestCreateGoal(APITestCase):

    def test_auth_required(self):
        response = self.client.post(reverse('create-goal'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_category_owner(self):
        user = User.objects.create(username='username', password='password')
        category = GoalCategory.objects.create(title='cat', user=user)

        self.client.force_login(user=User.objects.create(username='test_user', password='password'))
        response = self.client.post(
            path=reverse('create-goal'),
            data={
                'title': 'new goal',
                'category': category.id,
                'due_date': timezone.now(),
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_success(self):
        user = User.objects.create(username='username', password='password')
        category = GoalCategory.objects.create(title='cat', user=user)

        self.client.force_login(user=user)
        now = timezone.now()
        response = self.client.post(
            path=reverse('create-goal'),
            data={
                'title': 'new goal',
                'category': category.id,
                'due_date': now,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_goal = Goal.objects.last()
        self.assertDictEqual(
            response.json(),
            {
                'id': new_goal.id,
                'category': category.id,
                'created': timezone.localtime(new_goal.created).isoformat(),
                'updated': timezone.localtime(new_goal.updated).isoformat(),
                'title': 'new goal',
                'description': None,
                'status': Goal.Status.to_do.value,
                'priority': Goal.Priority.medium.value,
                'due_date': timezone.localtime(now).isoformat(),
            }
        )


class TestGoalsList(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='username', password='password')

    def test_auth_required(self):
        response = self.client.get(reverse('list-goals'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleted_category(self):
        Goal.objects.create(
            title='goal',
            category=GoalCategory.objects.create(title='cat', user=self.user, is_deleted=True),
            user=self.user,
            due_date=timezone.now()
        )

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('list-goals'), {'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_archived_goal(self):
        Goal.objects.create(
            title='goal',
            category=GoalCategory.objects.create(title='cat', user=self.user),
            user=self.user,
            due_date=timezone.now(),
            status=Goal.Status.archived
        )

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('list-goals'), {'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_not_goal_owner(self):
        Goal.objects.create(
            title='goal_1',
            category=GoalCategory.objects.create(title='cat_1', user=self.user),
            user=self.user,
            due_date=timezone.now(),
        )

        self.client.force_login(user=User.objects.create(username='new_user_2', password='password'))
        response = self.client.get(reverse('list-goals'), {'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_success(self):
        cat_1 = GoalCategory.objects.create(title='cat_1', user=self.user)
        cat_2 = GoalCategory.objects.create(title='cat_1', user=self.user)

        now = timezone.now()

        Goal.objects.bulk_create([
            Goal(title='goal_1', category=cat_1, user=self.user, due_date=now),
            Goal(title='goal_2', category=cat_2, user=self.user, due_date=now)
        ])

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('list-goals'), {'limit': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)

    def test_filter_by_category(self):
        now = timezone.now()

        cat_1 = GoalCategory.objects.create(title='cat_1', user=self.user)
        cat_2 = GoalCategory.objects.create(title='cat_2', user=self.user)

        Goal.objects.bulk_create([
            Goal(title='goal_1', category=cat_1, user=self.user, due_date=now),
            Goal(title='goal_2', category=cat_2, user=self.user, due_date=now)
        ])

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('list-goals'), {'limit': 10, 'category__in': cat_1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)


class TestRetrieveGoal(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='username', password='password')

    def test_auth_required(self):
        response = self.client.get(reverse('retrieve-update-destroy-goal', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_archived_goal(self):
        goal = Goal.objects.create(
            title='goal',
            category=GoalCategory.objects.create(title='cat', user=self.user),
            user=self.user,
            due_date=timezone.now(),
            status=Goal.Status.archived
        )

        self.client.force_login(user=self.user)
        response = self.client.get(reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_goal_owner(self):
        goal = Goal.objects.create(
            title='goal_1',
            category=GoalCategory.objects.create(title='cat_1', user=self.user),
            user=self.user,
            due_date=timezone.now(),
        )

        self.client.force_login(user=User.objects.create(username='new_user_2', password='password'))
        response = self.client.get(reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_success(self):
        category = GoalCategory.objects.create(title='cat_1', user=self.user)
        now = timezone.now()
        goal = Goal.objects.create(
            title='goal_1',
            category=category,
            user=self.user,
            due_date=now,
        )

        self.client.force_login(user=User.objects.create(username='new_user_2', password='password'))
        response = self.client.get(reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            {
                'id': goal.id,
                'category': category.id,
                'created': timezone.localtime(goal.created).isoformat(),
                'updated': timezone.localtime(goal.updated).isoformat(),
                'title': goal.title,
                'description': None,
                'status': Goal.Status.to_do.value,
                'priority': Goal.Priority.medium.value,
                'due_date': timezone.localtime(now).isoformat(),
                'user': self.user.id,
            }
        )


class TestUpdateGoal(APITestCase):

    def test_not_goal_owner(self):
        user = User.objects.create(username='username', password='password')
        goal = Goal.objects.create(
            title='goal_1',
            category=GoalCategory.objects.create(title='cat_1', user=user),
            user=user,
            due_date=timezone.now(),
        )

        self.client.force_login(user=User.objects.create(username='test_user', password='password'))
        response = self.client.patch(
            path=reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}),
            data={'title': 'new goal title'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_cat_owner(self):
        user_1, user_2 = User.objects.bulk_create([
            User(username='username_1', password='password'),
            User(username='username_2', password='password')
        ])
        cat_1, cat_2 = GoalCategory.objects.bulk_create([
            GoalCategory(title='cat_1', user=user_1),
            GoalCategory(title='cat_2', user=user_2),
        ])

        goal = Goal.objects.create(
            title='goal_1',
            category=cat_1,
            user=user_1,
            due_date=timezone.now(),
        )

        self.client.force_login(user=user_1)
        response = self.client.patch(
            path=reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}),
            data={'category': cat_2.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cat_not_found(self):
        user = User.objects.create(username='user', password='password')
        cat = GoalCategory.objects.create(title='cat', user=user)
        goal = Goal.objects.create(
            title='goal_1',
            category=cat,
            user=user,
            due_date=timezone.now(),
        )

        self.client.force_login(user=user)
        response = self.client.patch(
            path=reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}),
            data={'category': cat.id + 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success(self):
        user = User.objects.create(username='user', password='password')
        cat = GoalCategory.objects.create(title='cat', user=user)
        goal = Goal.objects.create(
            title='goal_1',
            category=cat,
            user=user,
            due_date=timezone.now(),
        )

        self.client.force_login(user=user)
        response = self.client.patch(
            path=reverse('retrieve-update-destroy-goal', kwargs={'pk': goal.pk}),
            data={'title': 'new_goal_title'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        goal.refresh_from_db(fields=('title',))
        self.assertEqual(goal.title, 'new_goal_title')
