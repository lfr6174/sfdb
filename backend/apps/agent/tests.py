import pytest
from django.urls import reverse

from apps.agent.models import Agent


# Prevents: PersonsView.vue receiving organizations (should only list AgentType.PERSON)
@pytest.mark.django_db
def test_list_only_persons(api_client):
    Agent.objects.create(name="pkd", agent_type="person")
    Agent.objects.create(name="scp fundation", agent_type="organization")

    data = api_client.get(reverse("agent:person-list")).json()
    names = [item["name"] for item in data["results"]]

    assert "pkd" in names
    assert "scp fundation" not in names
