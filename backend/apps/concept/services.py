from django.db.models import Count

from apps.concept.models import Concept
from apps.concept.serializers import ConceptSerializer
from apps.work.serializers import WorkBriefSerializer


def get_random_spotlight_data() -> dict | None:
    """
    取得首頁 Spotlight 區塊所需的隨機 Concept 與其關聯的 Works。
    """
    # 1. 找出至少有一個關聯作品的隨機 Concept
    concept = (
        Concept.objects.annotate(works_count=Count("works", distinct=True))
        .filter(works_count__gt=0)
        .order_by("?")
        .first()
    )

    if not concept:
        return None

    # 2. 序列化 Concept 基本資料，並附加關聯作品
    data = ConceptSerializer(concept).data
    works = concept.works.prefetch_related("credits__agent").order_by("-year", "title")[:4]
    data["spotlight_works"] = WorkBriefSerializer(works, many=True).data

    return data
