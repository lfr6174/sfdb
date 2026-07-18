from datetime import date

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
                queryset=WorkCatalogue.objects.filter(catalogue__catalogue_type="award").select_related(
                    "catalogue", "category"
                ),
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
            "year": w.year,
            "genre": w.get_genre_display(),
            "work_length": w.get_work_length_display(),
            "roles": sorted({c.role.noun for c in w.agent_contributions}),
            "concepts": [{"name": c.name, "slug": c.slug} for c in w.concepts.all()[:3]],
            "awards": [
                {
                    "catalogue_id": wc.catalogue.id,
                    "title": wc.catalogue.title,
                    "year": wc.year,
                    "category": wc.category.name if wc.category else None,
                    "result": wc.result,
                }
                for wc in getattr(w, "award_catalogues", [])
            ],
        }
        for w in works
    ]


def _group_publications(publications):
    """Fold per-media rows of the same edition (title, subtitle, publisher, source) into one entry."""
    groups = {}
    for p in publications:
        groups.setdefault((p.title, p.subtitle, p.publisher_id, p.source), []).append(p)

    entries = []
    for members in groups.values():
        members.sort(key=lambda p: p.pub_date or date.max)  # earliest edition first, undated last
        first = members[0]
        entries.append(
            {
                "ids": [p.id for p in members],
                "title": first.title,
                "year": first.year,
                "media": list(dict.fromkeys(p.composite_media_display for p in members)),
                "publisher": first.publisher.name if first.publisher else "",
                "roles": sorted({c.role.noun for p in members for c in p.agent_contributions}),
            }
        )

    entries.sort(key=lambda e: e["year"] or 0, reverse=True)  # newest first, undated last
    return entries


def get_agent_publications(agent):
    """Return publications the agent has participated in, media variants folded together"""

    publications = (
        Publication.objects.filter(agents=agent)
        .select_related("publisher")
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

    return _group_publications(publications)
