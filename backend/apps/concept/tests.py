import pytest
from django.urls import reverse

from apps.concept.models import Concept, ConceptAlias, ConceptCategory
from apps.work.models import Work, WorkConcept, WorkGenre, WorkLength


# Prevents: HomeView.vue's spotlight failing due to missing nested byline
@pytest.mark.django_db
def test_concept_random_api_contract(api_client):
    c = Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)
    w = Work.objects.create(title="Test", genre=WorkGenre.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w, concept=c)

    data = api_client.get(reverse("concept:concept-random")).json()
    assert "random_works" in data and "byline" in data["random_works"][0]


@pytest.mark.django_db
def test_concept_random_prefers_concepts_with_min_works(api_client):
    c1 = Concept.objects.create(name="Concept 1 Work", slug="c1", category=ConceptCategory.NOVUM)
    w1 = Work.objects.create(title="Work 1", genre=WorkGenre.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w1, concept=c1)

    c2 = Concept.objects.create(name="Concept 4 Works", slug="c4", category=ConceptCategory.NOVUM)
    for i in range(4):
        w = Work.objects.create(title=f"Work C4 {i}", genre=WorkGenre.NOVEL, work_length=WorkLength.LONG)
        WorkConcept.objects.create(work=w, concept=c2)

    # If the logic prefers concepts with >= 4 works, c2 should be selected every time.
    # Without the logic, c1 would be selected roughly 50% of the time.
    for _ in range(5):
        data = api_client.get(reverse("concept:concept-random")).json()
        assert data["slug"] == c2.slug


# Prevents: ConceptDetailView.vue missing the manually mapped 'work_title'
@pytest.mark.django_db
def test_concept_retrieve_manual_dict_contract(api_client):
    c = Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)
    w = Work.objects.create(title="TargetWork", genre=WorkGenre.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w, concept=c, description="Desc")

    data = api_client.get(reverse("concept:concept-detail", kwargs={"slug": c.slug})).json()
    assert data["work_concepts"][0]["work_title"] == "TargetWork"


@pytest.mark.django_db
def test_concept_search_matches_aliases(api_client):
    c = Concept.objects.create(name="賽博龐克", slug="cp", category=ConceptCategory.NOVUM)
    ConceptAlias.objects.create(concept=c, name="Cyberpunk")

    data = api_client.get(reverse("concept:concept-list"), {"search": "Cyberpunk"}).json()
    assert [r["slug"] for r in data["results"]] == ["cp"]


# Prevents: searching across the aliases reverse-FK join producing duplicate rows.
@pytest.mark.django_db
def test_concept_search_aliases_no_duplicates(api_client):
    c = Concept.objects.create(name="賽博龐克", slug="cp", category=ConceptCategory.NOVUM)
    ConceptAlias.objects.create(concept=c, name="Cyberpunk")
    ConceptAlias.objects.create(concept=c, name="Cyber punk")

    data = api_client.get(reverse("concept:concept-list"), {"search": "Cyber"}).json()
    assert [r["slug"] for r in data["results"]] == ["cp"]


@pytest.mark.django_db
def test_concept_detail_exposes_aliases_in_order(api_client):
    c = Concept.objects.create(name="賽博龐克", slug="cp", category=ConceptCategory.NOVUM)
    ConceptAlias.objects.create(concept=c, name="Second", order=2)
    ConceptAlias.objects.create(concept=c, name="First", order=1)

    data = api_client.get(reverse("concept:concept-detail", kwargs={"slug": c.slug})).json()
    assert [a["name"] for a in data["aliases"]] == ["First", "Second"]


# Prevents: frontend keeping its own category-value → label map (drifts when
# backend adds or renames a category); group headers come from category_display
@pytest.mark.django_db
def test_concept_list_exposes_category_display(api_client):
    Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)

    data = api_client.get(reverse("concept:concept-list")).json()
    assert data["results"][0]["category_display"] == "新異 Novum"
