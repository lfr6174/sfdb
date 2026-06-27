from django.core.management.base import BaseCommand
from django.db import transaction

from apps.agent.models import Agent
from apps.work.models import Role

# 初始資料清單 依部署需求自行增修
ROLES = [
    {"code": "author", "verb": "著", "noun": "作者", "order": 10},
    {"code": "illustrator", "verb": "繪", "noun": "繪師", "order": 20},
    {"code": "translator", "verb": "譯", "noun": "譯者", "order": 30},
    {"code": "narrator", "verb": "述", "noun": "旁白", "order": 40},
]

PUBLISHERS = [
    "二魚文化",
    "幻華創造",
    "洪範",
    "聯經",
    "聯合文學",
    "蓋亞",
    "遠流",
    "麥田",
    "華騰文化",
    "獨步文化",
    "臉譜",
]


class Command(BaseCommand):
    help = "載入初始參考資料（冪等，可重複執行）。"

    @transaction.atomic
    def handle(self, *args, **options):
        for r in ROLES:
            Role.objects.update_or_create(code=r["code"], defaults=r)
        for name in PUBLISHERS:
            Agent.objects.get_or_create(name=name, defaults={"agent_type": Agent.AgentType.ORGANIZATION})
        self.stdout.write(self.style.SUCCESS(f"已載入 {len(ROLES)} 項職責、{len(PUBLISHERS)} 個出版社。"))
