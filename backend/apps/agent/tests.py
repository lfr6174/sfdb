# Create your tests here.
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.agent.models import Agent


# Guarantees PersonsView.vue lists only AgentType.PERSON
@pytest.mark.django_db
def test_list_only_persons():
    Agent.objects.create(name="pkd", agent_type="person")
    Agent.objects.create(name="scp fundation", agent_type="organization")

    response = APIClient().get("/api/persons/")
    assert response.status_code == status.HTTP_200_OK

    assert "results" in response.data
    results = response.data["results"]

    names = [item["name"] for item in results]
    assert "pkd" in names
    assert "scp fundation" not in names
