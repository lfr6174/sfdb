from django.db import models

from apps.core.models import TimeStampedModel

# ============================================================================
# WORK
# Core entities representing abstract artistic creations and their relationships.
# ============================================================================


class Series(TimeStampedModel):
    """
    A cohesive series of works, e.g. Foundation Series".
    """

    title = models.CharField(max_length=300, verbose_name="系列名稱")
    note = models.TextField(blank=True, verbose_name="備註")

    class Meta:
        verbose_name = "系列"
        verbose_name_plural = "系列"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Language(models.TextChoices):
    """Language categories for works and publications."""

    ZH_HANT = "zh-hant", "繁體中文"
    ZH_HANS = "zh-hans", "簡體中文"
    EN = "en", "英文"
    JA = "ja", "日文"
    OTHER = "other", "其他"


class MediaType(models.TextChoices):
    """Media types for a work."""

    NOVEL = "novel", "小說"
    COMIC = "comic", "漫畫"


class WorkLength(models.TextChoices):
    """Length categories for a work."""

    LONG = "long", "長篇"
    SHORT = "short", "中短篇"


class WorkProvenance(models.TextChoices):
    """Provenance for a work"""

    ORIGINAL = "original", "原創"
    LICENSED = "licensed", "代理"


class Work(TimeStampedModel):
    """
    Core entity: Work.
    Represents an abstract artistic or literary creation,
    independent of its specific publication or release format.
    """

    title = models.CharField(max_length=300, verbose_name="標題")
    media_type = models.CharField(max_length=20, choices=MediaType.choices, verbose_name="媒體類型")
    work_length = models.CharField(max_length=20, choices=WorkLength.choices, verbose_name="篇幅")
    provenance = models.CharField(max_length=20, choices=WorkProvenance.choices, verbose_name="作品來源")
    language = models.CharField(
        max_length=20, choices=Language.choices, default=Language.ZH_HANT, verbose_name="原始語言"
    )
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="發表年份")
    description = models.TextField(blank=True, verbose_name="無劇透概述 (Synopsis)")

    series = models.ForeignKey(
        Series,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="works",
        verbose_name="所屬系列",
    )
    series_order = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="系列順序"
    )  # Use Decimal to support ordering like 1.5 for prequels or spin-offs

    persons = models.ManyToManyField(
        "person.Person", through="WorkCredit", related_name="works", verbose_name="相關人物"
    )
    concepts = models.ManyToManyField(
        "concept.Concept", through="WorkConcept", related_name="works", verbose_name="相關概念"
    )

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "作品"
        verbose_name_plural = "作品"

    def __str__(self):
        year_str = f" ({self.year})" if self.year else ""
        return f"{self.title}{year_str}"


class WorkRole(models.TextChoices):
    """Core contribution roles of a person at the 'Work' level."""

    AUTHOR = "author", "作者"
    CO_AUTHOR = "co_author", "合著"
    STORY = "story", "原作"
    ART = "art", "作畫"


class WorkCredit(models.Model):
    """
    Intermediate table mapping Works to Persons (records who created the work).
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="credits", verbose_name="作品")
    person = models.ForeignKey(
        "person.Person",
        on_delete=models.CASCADE,
        related_name="work_credits",
        verbose_name="人物",
    )
    role = models.CharField(max_length=20, choices=WorkRole.choices, verbose_name="角色")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="排序")

    class Meta:
        unique_together = [("work", "person", "role")]
        ordering = ["order"]
        verbose_name = "作品人物關聯"
        verbose_name_plural = "作品人物關聯"

    def __str__(self):
        return f"{self.work.title} - {self.person.name} ({self.get_role_display()})"


class WorkConcept(models.Model):
    """
    Intermediate table mapping Works to Concepts.
    Records how a specific concept is applied and interpreted in a work.
    All descriptions here are treated as spoilers by default in the UI.
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="work_concepts", verbose_name="作品")
    concept = models.ForeignKey(
        "concept.Concept",
        on_delete=models.CASCADE,
        related_name="work_concepts",
        verbose_name="概念",
    )
    description = models.TextField(blank=True, verbose_name="概念應用詳述", help_text="說明該概念在此作品中如何運作。")

    class Meta:
        unique_together = [("work", "concept")]
        verbose_name = "作品概念關聯"
        verbose_name_plural = "作品概念關聯"

    def __str__(self):
        return f"{self.work.title} ✕ {self.concept.name}"


# ============================================================================
# PUBLICATION
# Represents physical or digital releases and their specific contributors.
# ============================================================================


class Publisher(TimeStampedModel):
    """
    Represents a publishing or distributing company.
    """

    name = models.CharField(max_length=200, verbose_name="出版/發行商名稱")
    description = models.TextField(blank=True, verbose_name="概述")

    class Meta:
        verbose_name = "出版商"
        verbose_name_plural = "出版商"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PublicationMedia(models.TextChoices):
    """Publication medium."""

    BOOK = "book", "書籍"
    MAGAZINE = "magazine", "雜誌"
    NEWSPAPER = "newspaper", "報紙"
    WEBSITE = "website", "網站"
    OTHER = "other", "其它"


class Publication(TimeStampedModel):
    """
    Represents a specific physical or digital release of a Work.
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="publications", verbose_name="所屬作品")
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="publications",
        verbose_name="出版商",
    )
    title = models.CharField(max_length=300, verbose_name="名稱")
    language = models.CharField(
        max_length=20, choices=Language.choices, default=Language.ZH_HANT, verbose_name="出版品語言"
    )
    media = models.CharField(max_length=20, choices=PublicationMedia.choices, verbose_name="出版品媒體")
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="發行年份")
    isbn = models.CharField(max_length=50, blank=True, verbose_name="ISBN")
    note = models.CharField(max_length=200, blank=True, verbose_name="備註")

    persons = models.ManyToManyField(
        "person.Person", through="PublicationCredit", related_name="publications", verbose_name="相關人物"
    )

    class Meta:
        ordering = ["year", "title"]
        verbose_name = "出版品"
        verbose_name_plural = "出版品"

    def __str__(self):
        return f"{self.title} ({self.year})"


class PublicationRole(models.TextChoices):
    """Contribution roles of a person at the 'Publication' level."""

    AUTHOR = "author", "作者"
    CO_AUTHOR = "co_author", "合著"
    STORY = "story", "原作"
    ART = "art", "作畫"
    TRANSLATOR = "translator", "譯者"
    EDITOR = "editor", "編輯"
    ILLUSTRATOR = "illustrator", "插畫"


class PublicationCredit(models.Model):
    """
    Intermediate table mapping Publications to Persons (e.g., records who translated a specific edition).
    """

    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="credits", verbose_name="出版品"
    )
    person = models.ForeignKey(
        "person.Person",
        on_delete=models.CASCADE,
        related_name="publication_credits",
        verbose_name="人物",
    )
    display_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="顯示名稱",
        help_text="若此處留空，將會使用人物的本名。用於翻譯名稱或特定筆名。",
    )
    role = models.CharField(max_length=20, choices=PublicationRole.choices, verbose_name="角色")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="排序")

    class Meta:
        unique_together = [("publication", "person", "role")]
        ordering = ["order"]
        verbose_name = "出版品人物關聯"
        verbose_name_plural = "出版品人物關聯"

    def __str__(self):
        name_to_display = self.display_name or self.person.name
        return f"{self.publication.title} - {name_to_display} ({self.get_role_display()})"


# ============================================================================
# CATALOGUE
# Represents collections, awards, and reading lists.
# ============================================================================


class CatalogueType(models.TextChoices):
    AWARD = "award", "獎項"
    READING_LIST = "reading_list", "書單"
    ANTHOLOGY = "anthology", "選集"


class Catalogue(TimeStampedModel):
    """
    Represents external collections, literary awards, or reading lists.
    """

    title = models.CharField(max_length=300, verbose_name="名稱")
    catalogue_type = models.CharField(max_length=20, choices=CatalogueType.choices, verbose_name="類型")
    curator = models.ForeignKey(
        "person.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="curated_catalogues",
        verbose_name="維護者",
    )
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="年份")
    note = models.TextField(blank=True, verbose_name="備註")

    class Meta:
        verbose_name = "收錄目錄"
        verbose_name_plural = "收錄目錄"
        ordering = ["-year", "title"]

    def __str__(self):
        return f"{self.title} ({self.year})" if self.year else self.title


class CatalogueEntry(models.Model):
    """
    Intermediate table mapping Works to Catalogues.
    Records details of a work's inclusion in a list or its award status.
    """

    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, related_name="entries", verbose_name="所屬目錄")
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="catalogue_entries", verbose_name="作品")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="排序", help_text="在書單中的排名或順序")
    note = models.CharField(max_length=200, blank=True, verbose_name="收錄備註", help_text="例如：獲獎、提名、首獎")

    class Meta:
        unique_together = [("catalogue", "work")]
        ordering = ["order"]
        verbose_name = "目錄收錄紀錄"
        verbose_name_plural = "目錄收錄紀錄"

    def __str__(self):
        return f"[{self.note}] {self.work.title} in {self.catalogue.title}"
