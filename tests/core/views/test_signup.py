import random

import pytest
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_passwords_missmatch(client, faker):
    response = client.post(reverse('signup'), data={
        'username': faker.user_name(),
        'password': faker.password(),
        'password_repeat': faker.password(),
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'password_repeat': ['Passwords must match']}


@pytest.mark.django_db
@pytest.mark.parametrize('password_params', [
    {'length': random.randrange(4, MinimumLengthValidator().min_length)},
    None,
], ids=('min_length_validation', 'common_password_validation'))
def test_invalid_password(client, faker, password_params):
    if password_params:
        invalid_password = faker.password(**password_params)
    else:
        invalid_password = CommonPasswordValidator().passwords.pop()

    response = client.post(reverse('signup'), data={
        'username': faker.user_name(),
        'password': invalid_password,
        'password_repeat': invalid_password,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_success_short(client, django_user_model, faker):
    assert not django_user_model.objects.count()
    password = faker.password()
    response = client.post(reverse('signup'), data={
        'username': faker.user_name(),
        'password': password,
        'password_repeat': password,
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert django_user_model.objects.count() == 1
    user = django_user_model.objects.last()
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'first_name': '',
        'last_name': '',
        'email': '',
    }
    assert user.password != password
    assert user.check_password(password)


@pytest.mark.django_db
def test_success_full(client, django_user_model, faker):
    assert not django_user_model.objects.count()
    password = faker.password()
    response = client.post(reverse('signup'), data={
        'username': faker.user_name(),
        'first_name': faker.first_name(),
        'last_name': faker.last_name(),
        'email': faker.email(),
        'password': password,
        'password_repeat': password,
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert django_user_model.objects.count() == 1
    user = django_user_model.objects.last()
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
    assert user.password != password
    assert user.check_password(password)
