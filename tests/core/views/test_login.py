import pytest
from django.urls import reverse
from rest_framework import status

from todolist.core.models import User


@pytest.mark.django_db
def test_user_not_found(client, faker):
    response = client.post(reverse('login'), data={
        'username': faker.user_name(),
        'password': faker.password(),
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Incorrect authentication credentials.'}


@pytest.mark.django_db
def test_invalid_credentials(client, faker):
    user = User.objects.create_user(username=faker.user_name(), password=faker.password())
    response = client.post(reverse('login'), data={
        'username': user.username,
        'password': faker.password(),
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Incorrect authentication credentials.'}


@pytest.mark.django_db
@pytest.mark.parametrize('user_attrs', [
    {'email': 'test@test.com', 'first_name': 'Ivan', 'last_name': 'Ivanov'},
    {},
], ids=('full model', 'short model'))
def test_success(client, faker, user_attrs: dict):
    password = faker.password()
    user = User.objects.create_user(username=faker.user_name(), password=password, **user_attrs)
    response = client.post(reverse('login'), data={
        'username': user.username,
        'password': password,
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username
    }
