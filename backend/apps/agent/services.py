from django.db.models import Count, Prefetch, Q

from apps.concept.models import Concept
from apps.work.models import Publication, PublicationCredit, Work, WorkCredit


def get_agent_top_concepts(agent, limit: int = 7):
    """Return concepts related to agent's works, ordered by work count."""
    qs = (
        Concept.objects.filter(works__agents=agent)
        .annotate(works_count=Count("works", filter=Q(works__agents=agent), distinct=True))
        .order_by("-works_count")
    )

    return [{"id": c.id, "name": c.name, "slug": c.slug, "works_count": c.works_count} for c in qs[:limit]]


def get_agent_works(agent):
    """Return works the agent has contributed to"""

    works = (
        Work.objects.filter(credits__agent=agent)
        .prefetch_related(
            Prefetch("credits", queryset=WorkCredit.objects.filter(agent=agent), to_attr="agent_credits"),
            "concepts",
        )
        .distinct()
        .order_by("-year")
    )

    return [
        {
            "id": w.id,
            "title": w.title,
            "year": w.year,
            "media_type": w.get_media_type_display(),
            "work_length": w.get_work_length_display(),
            "roles": sorted({c.get_role_display() for c in w.agent_credits}),
            "concepts": [{"name": c.name, "slug": c.slug} for c in w.concepts.all()[:3]],
        }
        for w in works
    ]


def get_agent_publications(agent):
    """Return publications the agent has participated in"""

    publications = (
        Publication.objects.filter(credits__agent=agent)
        .prefetch_related(
            Prefetch("credits", queryset=PublicationCredit.objects.filter(agent=agent), to_attr="agent_credits")
        )
        .distinct()
        .order_by("-year")
    )

    return [
        {
            "id": p.id,
            "title": p.title,
            "year": p.year,
            "media": p.get_media_display(),
            "publisher": p.publisher.name if p.publisher else "",
            "isbn": p.isbn,
            "note": p.note,
            "roles": sorted({c.get_role_display() for c in p.agent_credits}),
        }
        for p in publications
    ]
