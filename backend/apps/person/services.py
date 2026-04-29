from collections import Counter


def calculate_person_concept_stats(person) -> list[dict]:
    """計算該人物參與過的所有作品中，各個概念出現的頻率。"""
    concept_counter = Counter()
    counted_work_ids = set()

    for credit in person.work_credits.all():
        work = credit.work
        if work.id not in counted_work_ids:
            counted_work_ids.add(work.id)
            for concept in work.concepts.all():
                concept_counter[(concept.name, concept.slug)] += 1

    return [{"name": name, "slug": slug, "count": count} for (name, slug), count in concept_counter.most_common()]


def build_participated_works_list(person) -> list[dict]:
    """彙整該人物參與過的作品列表，合併相同作品的不同角色。"""
    works_dict = {}

    for credit in person.work_credits.all():
        work = credit.work
        if work.id not in works_dict:
            works_dict[work.id] = {
                "id": work.id,
                "title": work.title,
                "title_en": getattr(work, "title_en", ""),
                "year": work.year,
                "media_type": work.get_media_type_display() if hasattr(work, "get_media_type_display") else "",
                "work_length": work.get_work_length_display() if hasattr(work, "get_work_length_display") else "",
                "roles": set(),
                "concepts": [{"name": c.name, "slug": c.slug} for c in work.concepts.all()[:3]],
            }
        works_dict[work.id]["roles"].add(credit.get_role_display())

    result = list(works_dict.values())
    for w in result:
        w["roles"] = sorted(list(w["roles"]))
    result.sort(key=lambda x: x["year"] if x["year"] is not None else 0, reverse=True)
    return result


def build_participated_publications_list(person) -> list[dict]:
    """彙整該人物參與過的出版品列表，合併相同出版品的不同角色。"""
    pubs_dict = {}

    for credit in person.publication_credits.all():
        publication = credit.publication
        if publication and publication.id not in pubs_dict:
            pubs_dict[publication.id] = {
                "id": publication.id,
                "title": publication.title,
                "year": publication.year,
                "media": publication.get_media_display() if hasattr(publication, "get_media_display") else "",
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
