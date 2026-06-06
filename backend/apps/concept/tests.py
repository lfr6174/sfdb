import pytest
from django.urls import reverse

from apps.concept.models import Concept, ConceptCategory
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
