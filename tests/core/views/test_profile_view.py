import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_auth_required(client):
    response = client.get(reverse('profile'))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_success(client, user, faker):
    user.first_name = faker.first_name()
    user.last_name = faker.last_name()
    user.save(update_fields=('first_name', 'last_name'))
    client.force_login(user)
    response = client.get(reverse('profile'))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
