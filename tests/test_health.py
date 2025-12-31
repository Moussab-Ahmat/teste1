import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_endpoint_returns_ok():
    client = APIClient()
    url = reverse('health')
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
