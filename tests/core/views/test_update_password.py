import random

import pytest
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_auth_required(client):
    response = client.patch(reverse('update-password'))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_invalid_old_password(client, user, faker):
    client.force_login(user)
    response = client.patch(reverse('update-password'), data={
        'old_password': faker.password(),
        'new_password': faker.password(),
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {'old_password': ['field is incorrect']}


@pytest.mark.django_db
@pytest.mark.parametrize('password_params', [
    {'length': random.randrange(4, MinimumLengthValidator().min_length)},
    None,
], ids=('min length validation', 'common password validation'))
def test_weak_new_password(client, user, faker, password_params):
    password = faker.password()
    user.set_password(password)
    user.save(update_fields=('password',))

    if password_params:
        new_password = faker.password(**password_params)
    else:
        new_password = CommonPasswordValidator().passwords.pop()

    client.force_login(user)
    response = client.patch(reverse('update-password'), data={
        'old_password': password,
        'new_password': new_password,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_success(client, user, faker):
    old_password = faker.password()
    user.set_password(old_password)
    user.save(update_fields=('password',))

    new_password = faker.password()
    client.force_login(user)
    response = client.patch(reverse('update-password'), data={
        'old_password': old_password,
        'new_password': new_password,
    })
    assert response.status_code == status.HTTP_200_OK
    assert not response.json()
    user.refresh_from_db(fields=('password',))
    assert user.check_password(new_password)
