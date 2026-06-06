from types import SimpleNamespace

import pytest
from django.urls import reverse

from apps.agent.models import Agent
from apps.concept.models import Concept
from apps.work.models import (
    Catalogue,
    CatalogueType,
    Manifestation,
    Publication,
    RelationKind,
    Role,
    Work,
    WorkAgent,
    WorkCatalogue,
    WorkConcept,
    WorkGenre,
    WorkLength,
    WorkRelation,
)
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
    w = Work.objects.create(title="W", genre=WorkGenre.NOVEL, work_length=WorkLength.SHORT)
    a = Agent.objects.create(name="A", agent_type="person")
    WorkAgent.objects.create(work=w, agent=a, role=Role.objects.create(code="r", noun="n", verb="v"))

    data = api_client.get(reverse("work:work-list")).json()["results"][0]
    expected = {"id", "title", "year", "byline", "genre_display", "work_length_display", "work_concepts"}
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


# Prevents: Filtering by publication or catalogue not matching exactly
@pytest.mark.django_db
def test_filter_works_by_publication_and_catalogue(api_client):
    w1, w2 = Work.objects.create(title="W1"), Work.objects.create(title="W2")
    pub = Publication.objects.create(title="Pub A")
    cat = Catalogue.objects.create(title="Cat A", catalogue_type=CatalogueType.AWARD)

    Manifestation.objects.create(work=w1, publication=pub)
    WorkCatalogue.objects.create(work=w2, catalogue=cat)

    # Test publication filter
    pub_data = api_client.get(reverse("work:work-list"), {"publication": pub.id}).json()
    assert pub_data["count"] == 1 and pub_data["results"][0]["title"] == "W1"

    # Test catalogue filter
    cat_data = api_client.get(reverse("work:work-list"), {"catalogue": cat.title}).json()
    assert cat_data["count"] == 1 and cat_data["results"][0]["title"] == "W2"


# Prevents: Multiple categories of the same work in a single catalogue
# (or multiple catalogues with same title) causing duplicate works in API response
@pytest.mark.django_db
def test_filter_by_catalogue_duplicate_entries_returns_distinct(api_client):
    w1 = Work.objects.create(title="Distinct Work")
    cat = Catalogue.objects.create(title="Cat with Duplicates", catalogue_type=CatalogueType.AWARD)

    # Same work appears twice in the same catalogue under different categories
    WorkCatalogue.objects.create(work=w1, catalogue=cat, category="Category 1")
    WorkCatalogue.objects.create(work=w1, catalogue=cat, category="Category 2")

    # Since we filter by title now
    data = api_client.get(reverse("work:work-list"), {"catalogue": cat.title}).json()
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Distinct Work"


# Prevents: Public write access and unintended auth requirements on GET
@pytest.mark.django_db
@pytest.mark.parametrize("method, expected", [("get", 200), ("post", 403), ("put", 403), ("delete", 403)])
def test_work_api_unauth_surface(api_client, method, expected):
    assert getattr(api_client, method)(reverse("work:work-list")).status_code == expected


# Prevents: Unnormalized undirected relations bypassing the database unique constraint
@pytest.mark.django_db
def test_work_relation_undirected_normalization():
    """Ensures undirected RELATED relations always save with subject_id < object_id to prevent mirroring duplicates."""
    w1 = Work.objects.create(title="W1")
    w2 = Work.objects.create(title="W2")

    smaller, larger = (w1, w2) if w1.id < w2.id else (w2, w1)

    rel1 = WorkRelation.objects.create(subject_work=larger, object_work=smaller, kind=RelationKind.RELATED)

    assert rel1.subject_work_id == smaller.id
    assert rel1.object_work_id == larger.id
