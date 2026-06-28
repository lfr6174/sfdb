from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TimeStampedModel


class ConceptCategory(models.TextChoices):
    NOVUM = "novum", "新異 (Novum)"
    NARRATIVE = "narrative", "敘事 (Narrative)"
    THEME = "theme", "主題 (Theme)"


class Concept(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="概念名稱")
    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name="URL 識別符",
        help_text="若有重複則為其添加分類前綴，例如 novum-cyberpunk。",
    )
    category = models.CharField(
        max_length=20, choices=ConceptCategory.choices, default=ConceptCategory.THEME, verbose_name="分類"
    )
    is_featured = models.BooleanField(default=False, verbose_name="精選標籤", help_text="是否顯示作品檢索頁側欄。")
    featured_order = models.PositiveIntegerField(default=0, verbose_name="側欄排序")

    description = models.TextField(blank=True, verbose_name="描述", help_text="解釋這個概念的定義或背景。可留空。")
    history = HistoricalRecords()

    related_concepts = models.ManyToManyField("self", blank=True, symmetrical=True, verbose_name="相關概念")

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "概念"
        verbose_name_plural = "概念"
        constraints = [models.UniqueConstraint(fields=["name", "category"], name="unique_concept_name_category")]
        indexes = [
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.name}"


class ConceptAlias(models.Model):
    """Other common names for a concept, such as translated names."""

    concept = models.ForeignKey(
        Concept,
        on_delete=models.CASCADE,
        related_name="aliases",
        verbose_name="概念",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="別名",
        help_text="此概念的其它稱呼，例如外文名或其它譯名。",
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name="顯示順序")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "概念別名"
        verbose_name_plural = "概念別名"
        constraints = [models.UniqueConstraint(fields=["concept", "name"], name="unique_concept_alias")]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.concept.name})"


class ConceptLink(models.Model):
    """External reference links for a concept (e.g., The Encyclopedia of Science Fiction)."""

    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="links", verbose_name="概念")
    title = models.CharField(max_length=200, help_text="e.g., SFE Entry, Wikipedia", verbose_name="連結標題")
    url = models.URLField(max_length=500, verbose_name="網址")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="排序")

    class Meta:
        ordering = ["order"]
        verbose_name = "概念連結"
        verbose_name_plural = "概念連結"
        constraints = [models.UniqueConstraint(fields=["concept", "url"], name="unique_concept_url")]

    def __str__(self):
        return f"{self.title} ({self.concept.name})"
