import pytest
from rest_framework.test import APIClient

from todolist.core.models import User


@pytest.fixture()
def client() -> APIClient:
    return APIClient()


@pytest.fixture()
def user(faker) -> User:
    user_data: dict[str, str] = {
        'username': faker.user_name(),
        'password': faker.password(),
    }
    if 'email' in User.REQUIRED_FIELDS:
        user_data['email'] = faker.email()

    return User.objects.create_user(**user_data)
