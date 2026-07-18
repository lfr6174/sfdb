from datetime import date
from types import SimpleNamespace

import pytest
from django.urls import reverse

from apps.agent.models import Agent
from apps.agent.services import _group_publications, get_agent_publications
from apps.work.models import Publication, PublicationAgent, Role


# Prevents: PersonsView.vue receiving organizations (should only list AgentType.PERSON)
@pytest.mark.django_db
def test_list_only_persons(api_client):
    Agent.objects.create(name="pkd", agent_type="person")
    Agent.objects.create(name="scp fundation", agent_type="organization")

    data = api_client.get(reverse("agent:person-list")).json()
    names = [item["name"] for item in data["results"]]

    assert "pkd" in names
    assert "scp fundation" not in names


def _pub(pk, media_label, pub_date, title="Book", subtitle="", publisher=None, source="book", roles=("繪師",)):
    return SimpleNamespace(
        id=pk,
        title=title,
        subtitle=subtitle,
        publisher=publisher,
        publisher_id=publisher.id if publisher else None,
        source=source,
        pub_date=pub_date,
        year=pub_date.year if pub_date else None,
        composite_media_display=media_label,
        agent_contributions=[SimpleNamespace(role=SimpleNamespace(noun=noun)) for noun in roles],
    )


# Prevents: one book released as print/digital/audio showing as duplicate rows on the person page
def test_group_publications_folds_media_editions():
    grouped = _group_publications(
        [
            _pub(1, "紙本書", date(2020, 1, 1)),
            _pub(2, "電子書", date(2021, 6, 1), roles=("繪師", "作者")),
            _pub(3, "有聲書", None),
        ]
    )

    assert grouped == [
        {
            "ids": [1, 2, 3],  # release order, undated last
            "title": "Book",
            "year": 2020,  # first release
            "media": ["紙本書", "電子書", "有聲書"],
            "publisher": "",
            "roles": ["作者", "繪師"],
        }
    ]


# Prevents: same-title books from different publishers (or re-editions with their own
# subtitle) being merged, and wrong page order
def test_group_publications_keeps_distinct_editions_and_sorts_newest_first():
    gaea = SimpleNamespace(id=1, name="蓋亞")
    grouped = _group_publications(
        [
            _pub(1, "紙本書", date(2018, 1, 1), title="Old"),
            _pub(2, "紙本書", date(2022, 1, 1), title="New"),
            _pub(3, "紙本書", None, title="Undated"),
            _pub(4, "紙本書", date(2022, 3, 1), title="New", publisher=gaea),
            _pub(5, "紙本書", date(2022, 6, 1), title="New", subtitle="新版"),
        ]
    )

    # ids identify each expected group: plain New, gaea's New, subtitled New, Old, Undated
    assert [e["ids"] for e in grouped] == [[2], [4], [5], [1], [3]]


# Prevents: a book and a same-title periodical/website being folded into one hybrid row
def test_group_publications_does_not_merge_across_sources():
    grouped = _group_publications(
        [
            _pub(1, "紙本書", date(2019, 1, 1), title="國語日報"),
            _pub(2, "報紙", date(2012, 1, 1), title="國語日報", source="newspaper"),
        ]
    )

    assert len(grouped) == 2


# Prevents: Prefetch leaking co-contributors' roles into the person's own role list
@pytest.mark.django_db
def test_get_agent_publications_scopes_roles_to_agent():
    illustrator = Agent.objects.create(name="畫家")
    author = Agent.objects.create(name="作者")
    draw = Role.objects.create(code="illustrator", verb="繪", noun="繪師", order=1)
    write = Role.objects.create(code="author", verb="著", noun="作者", order=2)

    print_ed = Publication.objects.create(title="Book", media="print", pub_date=date(2020, 1, 1))
    digital_ed = Publication.objects.create(title="Book", media="digital", pub_date=date(2021, 1, 1))
    for pub in (print_ed, digital_ed):
        PublicationAgent.objects.create(publication=pub, agent=illustrator, role=draw)
        PublicationAgent.objects.create(publication=pub, agent=author, role=write)

    entries = get_agent_publications(illustrator)

    assert len(entries) == 1
    assert entries[0]["ids"] == [print_ed.id, digital_ed.id]
    assert entries[0]["roles"] == ["繪師"]
