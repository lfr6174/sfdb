from datetime import date
from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.agent.models import Agent
from apps.concept.models import Concept
from apps.work.models import (
    Catalogue,
    CatalogueType,
    Category,
    Cycle,
    EncodingLevel,
    Manifestation,
    Publication,
    RelationKind,
    Role,
    Series,
    SeriesPublication,
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


# Prevents: an invalid cycle id silently falling back to the unfiltered list
# (django-filter's default ModelChoiceFilter validates the id exists before
# filtering; the explicit NumberFilter override must not)
@pytest.mark.django_db
def test_filter_works_by_cycle(api_client):
    cycle = Cycle.objects.create(title="Foundation Series")
    in_cycle = Work.objects.create(title="In Cycle", cycle=cycle)
    Work.objects.create(title="No Cycle")

    data = api_client.get(reverse("work:work-list"), {"cycle": cycle.id}).json()
    assert data["count"] == 1 and data["results"][0]["title"] == in_cycle.title

    data = api_client.get(reverse("work:work-list"), {"cycle": cycle.id + 1000}).json()
    assert data["count"] == 0


# Prevents: person-page merged rows (?publication=1,2) missing works,
# or a work collected in both listed editions appearing twice
@pytest.mark.django_db
def test_filter_works_by_multiple_publications_returns_distinct_union(api_client):
    novel = Work.objects.create(title="Novel")
    other = Work.objects.create(title="Other")
    print_ed = Publication.objects.create(title="Novel", media="print")
    digital_ed = Publication.objects.create(title="Novel", media="digital")

    Manifestation.objects.create(work=novel, publication=print_ed)
    Manifestation.objects.create(work=novel, publication=digital_ed)
    Manifestation.objects.create(work=other, publication=Publication.objects.create(title="Other"))

    data = api_client.get(reverse("work:work-list"), {"publication": f"{print_ed.id},{digital_ed.id}"}).json()
    assert data["count"] == 1
    assert data["results"][0]["title"] == "Novel"


# Prevents: Multiple categories of the same work in a single catalogue
# (or multiple catalogues with same title) causing duplicate works in API response
@pytest.mark.django_db
def test_filter_by_catalogue_duplicate_entries_returns_distinct(api_client):
    w1 = Work.objects.create(title="Distinct Work")
    cat = Catalogue.objects.create(title="Cat with Duplicates", catalogue_type=CatalogueType.AWARD)

    # Same work appears twice in the same catalogue under different categories
    cat1 = Category.objects.create(catalogue=cat, name="Category 1")
    cat2 = Category.objects.create(catalogue=cat, name="Category 2")
    WorkCatalogue.objects.create(work=w1, catalogue=cat, category=cat1)
    WorkCatalogue.objects.create(work=w1, catalogue=cat, category=cat2)

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


# Prevents: encoding_level facet filter breaking silently on the new four-level enum
@pytest.mark.django_db
def test_filter_works_by_encoding_level(api_client):
    Work.objects.create(title="Minimal", encoding_level=EncodingLevel.MINIMAL)
    Work.objects.create(title="Secondary", encoding_level=EncodingLevel.SECONDARY)
    partial = Work.objects.create(title="Partial", encoding_level=EncodingLevel.PARTIAL)
    full = Work.objects.create(title="Full", encoding_level=EncodingLevel.FULL)

    data = api_client.get(reverse("work:work-list"), {"encoding_level": "partial,full"}).json()
    assert {r["title"] for r in data["results"]} == {partial.title, full.title}


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


# Prevents: LimitedSearchFilter regression — oversized search terms must not raise 500
@pytest.mark.django_db
def test_search_long_input_returns_200(api_client):
    response = api_client.get(reverse("work:work-list"), {"search": "a" * 500})
    assert response.status_code == 200


# Prevents: concepts_in with many IDs bypassing the [:20] cap and causing complex JOIN
@pytest.mark.django_db
def test_concepts_in_large_list_returns_200(api_client):
    response = api_client.get(reverse("work:work-list"), {"concepts_in": ",".join(str(i) for i in range(100))})
    assert response.status_code == 200


# Prevents: frontend deriving total pages from a hardcoded page size (drifts when PAGE_SIZE changes)
@pytest.mark.django_db
def test_paginated_response_includes_total_pages(api_client):
    Work.objects.bulk_create([Work(title=f"W{i}") for i in range(21)])  # one past a full page of 20

    data = api_client.get(reverse("work:work-list")).json()
    assert data["count"] == 21
    assert data["total_pages"] == 2


# Prevents: works with no date heading the list. Both directions are checked because
# Postgres and SQLite default NULLs to opposite ends, so each one only breaks one way.
@pytest.mark.django_db
@pytest.mark.parametrize("ordering", ["ori_date", "-ori_date"])
def test_undated_works_sort_last(api_client, ordering):
    Work.objects.create(title="Undated")
    Work.objects.create(title="Early", ori_date=date(1979, 9, 1))
    Work.objects.create(title="Late", ori_date=date(2025, 12, 1))

    data = api_client.get(reverse("work:work-list"), {"ordering": ordering}).json()
    assert [r["title"] for r in data["results"]][-1] == "Undated"


# Prevents: a publication silently losing membership in one of its series (the point of the M2M
# switch), and API shape drift breaking WorkDetailView's pubLink (frontend reads series[0])
@pytest.mark.django_db
def test_publication_in_multiple_series(api_client):
    work = Work.objects.create(title="W")
    pub = Publication.objects.create(title="Pub")
    Manifestation.objects.create(work=work, publication=pub)
    collected_works = Series.objects.create(title="作品集")
    imprint = Series.objects.create(title="叢書")
    SeriesPublication.objects.create(series=collected_works, publication=pub, code="7")
    SeriesPublication.objects.create(series=imprint, publication=pub, code="E010")

    data = api_client.get(reverse("work:work-detail", kwargs={"pk": work.id})).json()
    series_data = data["publications"][0]["series"]
    assert {(s["id"], s["title"], s["code"]) for s in series_data} == {
        (collected_works.id, "作品集", "7"),
        (imprint.id, "叢書", "E010"),
    }

    for series in (collected_works, imprint):
        filtered = api_client.get(reverse("work:work-list"), {"publication_series": series.id}).json()
        assert filtered["count"] == 1 and filtered["results"][0]["title"] == "W"


# Prevents: cross-publisher series mix-ups (e.g. picking the wrong "文學森林") going unnoticed,
# while still allowing legitimate entries where either side's publisher is unset
@pytest.mark.django_db
def test_series_publisher_mismatch_rejected():
    sanmin = Agent.objects.create(name="三民", agent_type="organization")
    new_experience = Agent.objects.create(name="新經典文化", agent_type="organization")
    series = Series.objects.create(title="文學森林", publisher=sanmin)
    pub = Publication.objects.create(title="Pub", publisher=new_experience)

    with pytest.raises(ValidationError):
        SeriesPublication(series=series, publication=pub).full_clean()

    # Either side left blank must not be blocked by the consistency check.
    pub_no_publisher = Publication.objects.create(title="Pub2")
    SeriesPublication(series=series, publication=pub_no_publisher).full_clean()
