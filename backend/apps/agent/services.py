from django.db.models import Count, Prefetch, Q

from apps.concept.models import Concept
from apps.work.models import Publication, PublicationAgent, Work, WorkAgent, WorkCatalogue


def get_agent_concepts(agent):
    """Return all concepts related to agent's works, ordered by work count."""
    qs = (
        Concept.objects.filter(works__agents=agent)
        .annotate(works_count=Count("works", filter=Q(works__agents=agent), distinct=True))
        .order_by("-works_count", "name")
    )

    return [{"id": c.id, "name": c.name, "slug": c.slug, "works_count": c.works_count} for c in qs]


def get_agent_works(agent):
    """Return works the agent has contributed to"""

    works = (
        Work.objects.filter(agents=agent)
        .prefetch_related(
            Prefetch(
                "contributions",
                queryset=WorkAgent.objects.filter(agent=agent).select_related("role"),
                to_attr="agent_contributions",
            ),
            "concepts",
            Prefetch(
                "work_catalogues",
                queryset=WorkCatalogue.objects.filter(catalogue__catalogue_type="award").select_related("catalogue"),
                to_attr="award_catalogues",
            ),
        )
        .distinct()
        .order_by("-ori_date")
    )

    return [
        {
            "id": w.id,
            "title": w.title,
            "year": w.ori_date.year if w.ori_date else None,
            "genre": w.get_genre_display(),
            "work_length": w.get_work_length_display(),
            "roles": sorted({c.role.noun for c in w.agent_contributions}),
            "concepts": [{"name": c.name, "slug": c.slug} for c in w.concepts.all()[:3]],
            "awards": [
                {
                    "catalogue_id": wc.catalogue.id,
                    "title": wc.catalogue.title,
                    "year": wc.catalogue.year,
                    "category": wc.category,
                    "status": wc.get_status_display(),
                }
                for wc in getattr(w, "award_catalogues", [])
            ],
        }
        for w in works
    ]


def get_agent_publications(agent):
    """Return publications the agent has participated in"""

    publications = (
        Publication.objects.filter(agents=agent)
        .prefetch_related(
            Prefetch(
                "contributions",
                queryset=PublicationAgent.objects.filter(agent=agent).select_related("role"),
                to_attr="agent_contributions",
            )
        )
        .distinct()
        .order_by("-pub_date")
    )

    return [
        {
            "id": p.id,
            "title": p.title,
            "year": p.pub_date.year if p.pub_date else None,
            "source": p.get_source_display(),
            "media": p.composite_media_display,
            "publisher": p.publisher.name if p.publisher else "",
            "isbn": p.isbn,
            "note": p.note,
            "roles": sorted({c.role.noun for c in p.agent_contributions}),
        }
        for p in publications
    ]
