# file: apps/agent/services.py
# description: These functions are migrated from the original 'person' app.
# They now operate on the 'Agent' model instead of 'Person'.

from collections import Counter


def calculate_agent_concept_stats(agent) -> list[dict]:
    """
    Calculate the frequency of each concept in all works the agent has participated in.
    (Migrated from person.services.calculate_person_concept_stats)
    """
    concept_counter = Counter()
    counted_work_ids = set()

    # The related_name 'work_credits' is now available on the Agent model
    for credit in agent.work_credits.all():
        work = credit.work
        if work.id not in counted_work_ids:
            counted_work_ids.add(work.id)
            for concept in work.concepts.all():
                concept_counter[(concept.name, concept.slug)] += 1

    return [{"name": name, "slug": slug, "count": count} for (name, slug), count in concept_counter.most_common()]


def build_participated_works_list(agent) -> list[dict]:
    """
    Compile a list of works the agent has participated in, merging different roles for the same work.
    (Migrated from person.services.build_participated_works_list)
    """
    works_dict = {}

    # The related_name 'work_credits' is now available on the Agent model
    for credit in agent.work_credits.all():
        work = credit.work
        if work.id not in works_dict:
            works_dict[work.id] = {
                "id": work.id,
                "title": work.title,
                "title_en": getattr(work, "title_en", ""),
                "year": work.year,
                "media_type": work.get_media_type_display(),
                "work_length": work.get_work_length_display(),
                "roles": set(),
                "concepts": [{"name": c.name, "slug": c.slug} for c in work.concepts.all()[:3]],
            }
        works_dict[work.id]["roles"].add(credit.get_role_display())

    result = list(works_dict.values())
    for w in result:
        w["roles"] = sorted(list(w["roles"]))
    result.sort(key=lambda x: x["year"] if x["year"] is not None else 0, reverse=True)
    return result


def build_participated_publications_list(agent) -> list[dict]:
    """
    Compile a list of publications the agent has participated in, merging different roles for the same publication.
    (Migrated from person.services.build_participated_publications_list)
    """
    pubs_dict = {}

    # The related_name 'publication_credits' is now available on the Agent model
    for credit in agent.publication_credits.all():
        publication = credit.publication
        if publication and publication.id not in pubs_dict:
            pubs_dict[publication.id] = {
                "id": publication.id,
                "title": publication.title,
                "year": publication.year,
                "media": publication.get_media_display(),
                "publisher": publication.publisher.name if publication.publisher else "",
                "isbn": publication.isbn,
                "note": publication.note,
                "roles": set(),
            }
        if publication:
            pubs_dict[publication.id]["roles"].add(credit.get_role_display())

    result = list(pubs_dict.values())
    for p in result:
        p["roles"] = sorted(list(p["roles"]))
    result.sort(key=lambda x: x["year"] if x["year"] is not None else 0, reverse=True)
    return result
