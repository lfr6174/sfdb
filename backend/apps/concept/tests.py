import pytest
from django.urls import reverse

from apps.concept.models import Concept, ConceptCategory
from apps.work.models import MediaType, Work, WorkConcept, WorkLength


# Prevents: HomeView.vue's spotlight failing due to missing nested byline
@pytest.mark.django_db
def test_concept_random_api_contract(api_client):
    c = Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)
    w = Work.objects.create(title="Test", media_type=MediaType.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w, concept=c)

    data = api_client.get(reverse("concept:concept-random")).json()
    assert "random_works" in data and "byline" in data["random_works"][0]


# Prevents: ConceptDetailView.vue missing the manually mapped 'work_title'
@pytest.mark.django_db
def test_concept_retrieve_manual_dict_contract(api_client):
    c = Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)
    w = Work.objects.create(title="TargetWork", media_type=MediaType.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w, concept=c, description="Desc")

    data = api_client.get(reverse("concept:concept-detail", kwargs={"slug": c.slug})).json()
    assert data["work_concepts"][0]["work_title"] == "TargetWork"
