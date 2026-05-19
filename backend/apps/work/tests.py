from types import SimpleNamespace

import pytest
from django.urls import reverse

from apps.agent.models import Agent
from apps.concept.models import Concept
from apps.work.models import MediaType, Role, Work, WorkAgent, WorkConcept, WorkLength
from apps.work.services import get_byline, get_credits


# Prevents: get_byline returning duplicate agents when missing Pen Names
def test_get_byline_deduplicates_and_falls_back():
    c1 = SimpleNamespace(agent=SimpleNamespace(id=1, name="A", agent_type="person"), display_name="Pen", role=True)
    c2 = SimpleNamespace(agent=SimpleNamespace(id=1, name="A", agent_type="person"), display_name="", role=True)
    assert get_byline([c1, c2]) == [{"id": 1, "text": "Pen", "agent_type": "person"}]


# Prevents: get_credits failing to group agents by role correctly
def test_get_credits_grouping():
    c = SimpleNamespace(
        agent=SimpleNamespace(id=1, name="A", agent_type="person"), role=SimpleNamespace(verb="W"), display_name=""
    )
    assert get_credits([c, c]) == [{"role": "W", "agents": [{"id": 1, "text": "A", "agent_type": "person"}]}]


# Prevents: API response shape drift breaking the Vue frontend WorksView contract
@pytest.mark.django_db
def test_work_list_api_contract(api_client):
    w = Work.objects.create(title="W", media_type=MediaType.NOVEL, work_length=WorkLength.SHORT)
    a = Agent.objects.create(name="A", agent_type="person")
    WorkAgent.objects.create(work=w, agent=a, role=Role.objects.create(code="r", noun="n", verb="v"))

    data = api_client.get(reverse("work:work-list")).json()["results"][0]
    expected = {"id", "title", "year", "byline", "media_type_display", "work_length_display", "work_concepts"}
    assert set(data.keys()) == expected and data["byline"][0]["text"] == "A"


# Prevents: Custom 'concepts_in' filter silently breaking AND logic (returning OR logic instead)
@pytest.mark.django_db
def test_concepts_in_and_logic(api_client):
    c1, c2 = Concept.objects.create(name="A", slug="a"), Concept.objects.create(name="B", slug="b")
    w1, w2 = Work.objects.create(title="W1"), Work.objects.create(title="W2")
    WorkConcept.objects.bulk_create(
        [WorkConcept(work=w1, concept=c1), WorkConcept(work=w2, concept=c1), WorkConcept(work=w2, concept=c2)]
    )

    data = api_client.get(reverse("work:work-list"), {"concepts_in": f"{c1.id},{c2.id}"}).json()
    assert data["count"] == 1 and data["results"][0]["title"] == "W2"


# Prevents: N+1 query regression on heavily nested Work list
@pytest.mark.django_db
def test_work_list_query_ceiling(api_client, django_assert_max_num_queries):
    Work.objects.bulk_create([Work(title=f"W{i}") for i in range(5)])
    with django_assert_max_num_queries(5):  # Protects prefetch chains: contributions__agent, roles, work_concepts
        api_client.get(reverse("work:work-list"))


# Prevents: Public write access and unintended auth requirements on GET
@pytest.mark.django_db
@pytest.mark.parametrize("method, expected", [("get", 200), ("post", 403), ("put", 403), ("delete", 403)])
def test_work_api_unauth_surface(api_client, method, expected):
    assert getattr(api_client, method)(reverse("work:work-list")).status_code == expected
