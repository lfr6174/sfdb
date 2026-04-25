from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class ConceptCategory(models.TextChoices):
    """
    The three main categories of Sci-Fi concepts.
    """

    NOVUM = "novum", "新異 (Novum)"
    NARRATIVE = "narrative", "敘事 (Narrative)"
    THEME = "theme", "主題 (Theme)"


class ConceptGroup(TimeStampedModel):
    """
    Sub-categories used to group concepts together in the Concept Hub.
    Example: 'Time Manipulation' under the 'Novum' category.
    """

    name = models.CharField(max_length=100, verbose_name="子分類名稱")
    category = models.CharField(max_length=20, choices=ConceptCategory.choices, verbose_name="所屬大類")
    description = models.TextField(blank=True, verbose_name="群組概述")

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "概念子分類"
        verbose_name_plural = "概念子分類"
        unique_together = [["name", "category"]]

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class Concept(TimeStampedModel):
    """
    The core entity of the database. Acts as both a tag for 'Works' and a standalone
    encyclopedia entry.
    """

    name = models.CharField(max_length=100, verbose_name="概念名稱")
    slug = models.SlugField(
        max_length=150,
        unique=True,
        help_text="若有重複則為其添加分類前綴，例如 novum-cyberpunk。",
        verbose_name="URL 識別符",
    )
    category = models.CharField(max_length=20, choices=ConceptCategory.choices, verbose_name="分類")

    group = models.ForeignKey(
        ConceptGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="concepts",
        verbose_name="子分類",
        help_text="Optional grouping for the Concept Hub UI.",
    )

    description = models.TextField(
        blank=True,
        verbose_name="概述",
        help_text="若有外部連結則保持內容精簡。",
    )

    related_concepts = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=True,
        verbose_name="相關概念",
        help_text="Concepts that are closely related for horizontal exploration.",
    )

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "概念"
        verbose_name_plural = "概念"
        # Allow same name in different categories, but enforce uniqueness within a category
        unique_together = [["name", "category"]]

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"

    def clean(self):
        """
        Ensure the concept's category matches its group's category.
        """
        super().clean()
        if self.group and self.group.category != self.category:
            raise ValidationError({"group": "子分類的所屬大類必須與概念的大類一致！"})


class ConceptLink(models.Model):
    """
    External reference links for a concept (e.g., The Encyclopedia of Science Fiction).
    UI spec recommends a soft limit of 3 links per concept.
    """

    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name="links", verbose_name="概念")
    title = models.CharField(max_length=200, help_text="e.g., SFE Entry, Wikipedia", verbose_name="連結標題")
    url = models.URLField(max_length=500, verbose_name="網址")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="排序")

    class Meta:
        ordering = ["order"]
        verbose_name = "概念連結"
        verbose_name_plural = "概念連結"

    def __str__(self):
        return f"{self.title} ({self.concept.name})"
