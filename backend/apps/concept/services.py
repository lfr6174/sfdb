import random

from django.db.models import Prefetch

from apps.concept.models import Concept
from apps.work.models import Work


def get_random_concept_with_works(max_works: int = 4):
    """Get a random concept with prefetched associated works."""

    ids = list(Concept.objects.filter(works__isnull=False).distinct().values_list("id", flat=True))

    if not ids:
        return None

    concept = Concept.objects.prefetch_related(
        Prefetch(
            "works",
            queryset=Work.objects.order_by("?")[:max_works],
            to_attr="random_works",
        )
    ).get(id=random.choice(ids))

    return concept
