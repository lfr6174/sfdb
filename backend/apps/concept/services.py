from apps.concept.models import Concept


def get_random_concept_with_works(max_works: int = 4):
    """Get a random concept with prefetched associated works."""

    concept = Concept.objects.filter(works__isnull=False).distinct().order_by("?").first()

    if not concept:
        return None

    concept.random_works = concept.works.order_by("?")[:max_works]

    return concept
