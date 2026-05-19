import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Protects against: Test code duplication for DRF APIClient."""
    return APIClient()
