import random

from django.db.models import Count, Prefetch

from apps.concept.models import Concept
from apps.work.models import Work


def get_random_concept_with_works(max_works: int = 6, min_works_required: int = 4):
    """Get a random concept with prefetched associated works."""
    ids = list(
        Concept.objects.annotate(num_works=Count("works"))
        .filter(num_works__gte=min_works_required)
        .values_list("id", flat=True)
    )

    if not ids:
        ids = list(Concept.objects.filter(works__isnull=False).distinct().values_list("id", flat=True))

    if not ids:
        return None

    concept = Concept.objects.prefetch_related(
        Prefetch(
            "works",
            queryset=Work.objects.prefetch_related(
                "contributions__agent",
                "contributions__role",
            )
            # NOTE: order_by('?') is intentionally used for random sampling,
            # but it can be slow on large tables. Consider caching or a more
            # scalable random selection strategy if the data grows.
            .order_by("?")[:max_works],
            to_attr="random_works",
        )
    ).get(id=random.choice(ids))

    return concept
