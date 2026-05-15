import pytest
from rest_framework.test import APIClient

from apps.concept.models import Concept, ConceptCategory
from apps.work.models import MediaType, Work, WorkConcept, WorkLength


# Guarantees HomeView.vue's spotlight always receives the nested byline
@pytest.mark.django_db
def test_concept_random_api_contract():
    c = Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)
    w = Work.objects.create(title="Test", media_type=MediaType.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w, concept=c)

    response = APIClient().get("/api/concepts/random/")
    assert "random_works" in response.data
    assert "byline" in response.data["random_works"][0]


# Guarantees ConceptDetailView.vue receives manually mapped 'work_title'
@pytest.mark.django_db
def test_concept_retrieve_manual_dict_contract():
    c = Concept.objects.create(name="Cyberpunk", slug="cp", category=ConceptCategory.NOVUM)
    w = Work.objects.create(title="TargetWork", media_type=MediaType.NOVEL, work_length=WorkLength.LONG)
    WorkConcept.objects.create(work=w, concept=c, description="Desc")

    response = APIClient().get(f"/api/concepts/{c.slug}/")
    assert response.data["work_concepts"][0]["work_title"] == "TargetWork"
