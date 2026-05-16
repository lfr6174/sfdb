from types import SimpleNamespace

import pytest
from rest_framework.test import APIClient

from apps.agent.models import Agent
from apps.work.models import MediaType, Role, Work, WorkAgent, WorkLength
from apps.work.services import get_byline, get_credits


# Guards against WorkDetailView.vue displaying duplicate agents or missing Pen Names
def test_get_byline_deduplicates_and_falls_back():
    c1 = SimpleNamespace(agent=SimpleNamespace(id=1, name="A", agent_type="person"), display_name="Pen", role=True)
    c2 = SimpleNamespace(agent=SimpleNamespace(id=1, name="A", agent_type="person"), display_name="", role=True)
    assert get_byline([c1, c2]) == [{"id": 1, "text": "Pen", "agent_type": "person"}]


# Ensures WorkDetailView.vue correctly groups credits (e.g., "Written by: Author")
def test_get_credits_grouping():
    c = SimpleNamespace(
        agent=SimpleNamespace(id=1, name="A", agent_type="person"), role=SimpleNamespace(verb="W"), display_name=""
    )
    assert get_credits([c, c]) == [{"role": "W", "agents": [{"id": 1, "text": "A", "agent_type": "person"}]}]


# Confirms to_representation and SerializerMethodFields are injecting Vue dependencies
@pytest.mark.django_db
def test_work_retrieve_api_contract():
    work = Work.objects.create(title="T", media_type=MediaType.NOVEL, work_length=WorkLength.LONG)
    response = APIClient().get(f"/api/works/{work.id}/")
    data = response.data
    # WorkDetailView.vue highly depends on these non-model injected fields
    assert all(k in data for k in ["byline", "credit", "publications", "work_catalogues"])


@pytest.mark.django_db
def test_work_list_api_contract():
    w = Work.objects.create(title="W", media_type=MediaType.NOVEL, work_length=WorkLength.SHORT)
    a1, a2 = Agent.objects.create(name="A1", agent_type="person"), Agent.objects.create(name="A2", agent_type="person")
    r1, r2 = Role.objects.create(code="r1", noun="n1", verb="v1"), Role.objects.create(code="r2", noun="n2", verb="v2")
    WorkAgent.objects.bulk_create([WorkAgent(work=w, agent=a1, role=r1), WorkAgent(work=w, agent=a2, role=r2)])
    data = APIClient().get("/api/works/").data["results"][0]
    assert "work_concepts" in data
    assert data["byline"] == [
        {"id": a1.id, "text": "A1", "agent_type": "person"},
        {"id": a2.id, "text": "A2", "agent_type": "person"},
    ]
