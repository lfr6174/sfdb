from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel

# ============================================================================
# WORK
# Core entities representing abstract artistic creations and their relationships.
# ============================================================================

# --- Enums ---


class Language(models.TextChoices):
    ZH_HANT = "zh-hant", "繁體中文"
    ZH_HANS = "zh-hans", "簡體中文"
    EN = "en", "英文"
    JA = "ja", "日文"
    OTHER = "other", "其他"


class MediaType(models.TextChoices):
    NOVEL = "novel", "小說"
    COMIC = "comic", "漫畫"


class WorkLength(models.TextChoices):
    LONG = "long", "長篇"
    SHORT = "short", "中短篇"


class WorkProvenance(models.TextChoices):
    ORIGINAL = "original", "原創"
    LICENSED = "licensed", "代理"


# --- Models ---


def validate_not_future_year(value):
    """Ensure the year is not in the future."""
    current_year = timezone.now().year
    limit = current_year + 1
    if value > limit:
        raise ValidationError("年份不得超過 %(limit)s 年。", params={"limit": limit})


def validate_isbn(value):
    """Validate ISBN format (10 or 13 digits) to ensure data integrity."""
    cleaned = value.replace("-", "").replace(" ", "")
    if cleaned and not (len(cleaned) in (10, 13) and cleaned[:-1].isdigit()):
        raise ValidationError("ISBN 長度必須為 10 或 13 碼純數字（可含連字號）。")


class Cycle(TimeStampedModel):
    """A collection of stories with similar themes or figures"""

    title = models.CharField(
        max_length=300,
        verbose_name="作品系列名稱",
        help_text="作品所屬的系列名稱，例如「基地系列」、「瀚星系列」、「火星三部曲」。",
    )
    note = models.TextField(
        blank=True, verbose_name="備註", help_text="任何補充說明，例如系列別名或歷史沿革。可留空。"
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "作品系列"
        verbose_name_plural = "作品系列"

    def __str__(self):
        return self.title


class Work(TimeStampedModel):
    """An abstract creation, independent of its specific format."""

    title = models.CharField(
        max_length=300,
        verbose_name="標題",
        help_text="作品最廣為人知的原文標題，例如 'Starship Troopers' 或「酔歩する男」。",
    )
    media_type = models.CharField(
        max_length=20, choices=MediaType.choices, verbose_name="體裁", help_text="作品的主要形式"
    )
    work_length = models.CharField(
        max_length=20,
        choices=WorkLength.choices,
        verbose_name="篇幅",
        help_text="長篇指單冊或多冊獨立成書的作品；中短篇則屬收錄於選集或期刊的作品。",
    )
    provenance = models.CharField(
        max_length=20,
        choices=WorkProvenance.choices,
        verbose_name="作品來源",
        help_text="「原創」指本土或與本土關係密切的作者創作（如陳浩基）；「代理」指從海外取得版權於本土出版的作品（如劉慈欣）。此欄位為主觀判斷。",
    )
    language = models.CharField(
        max_length=20,
        choices=Language.choices,
        default=Language.ZH_HANT,
        verbose_name="原始語言",
        help_text="作品最初發表時使用的語言。若作者採雙語發表，則各語系獨立登載。",
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[validate_not_future_year],
        verbose_name="首度發表年份",
        help_text="作品最早公開發表的年份，例如連載開始年或單行本初版年。不確定可留空。",
    )
    description = models.TextField(
        blank=True, verbose_name="作品簡介", help_text="簡要介紹作品，例如 logline 或 synopsis。可留空"
    )

    cycle = models.ForeignKey(
        Cycle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="works",
        verbose_name="所屬系列",
        help_text="若此作品屬於某個系列，請在此選取。獨立作品可留空。",
    )
    cycle_order = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="系列中的順序",
        help_text="作品在系列中的正式編號或建議閱讀順序，例如第一冊填「1」。前傳或外傳可使用小數，例如「1.5」。可留空。",
    )  # Use Decimal to support ordering like 1.5 for prequels or spin-offs

    agents = models.ManyToManyField(
        "agent.Agent",
        through="WorkAgent",
        related_name="works",
        verbose_name="人物/組織",
        blank=True,
    )
    concepts = models.ManyToManyField(
        "concept.Concept", through="WorkConcept", related_name="works", verbose_name="相關概念"
    )
    publications = models.ManyToManyField(
        "Publication", through="Manifestation", related_name="works", verbose_name="收錄於哪些出版物"
    )

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "作品"
        verbose_name_plural = "作品"

    def __str__(self):
        year_str = f" ({self.year})" if self.year else ""
        return f"{self.title}{year_str}"

    def clean(self):
        super().clean()
        if self.cycle_order is not None and self.cycle_id is None:
            raise ValidationError({"cycle_order": "請先填寫所屬系列，再登記其順序。"})


class Role(models.Model):
    """
    Function provided by a contributor, e.g., author, illustrator, etc.
    https://id.loc.gov/ontologies/bibframe.html#Role
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="職責代號",
        help_text="僅供程式內部識別用，使用英文小寫與底線，例如：illustrator、cover_designer。不會對外顯示。",
    )
    verb = models.CharField(
        max_length=10,
        verbose_name="動詞形式",
        help_text="接在人名後面使用，例如填「繪」，顯示時會呈現為「王小明 繪」。",
    )
    noun = models.CharField(
        max_length=10,
        verbose_name="名詞",
        help_text="接在職稱標題後使用，例如填「繪師」，顯示時會呈現為「繪師：王小明」。",
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="說明",
        help_text="在填表時顯示的補充說明，幫助填表者區分相近職責，例如「僅限小說封面插圖，漫畫作畫請用『畫』」。可留空。",
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name="顯示順序", help_text="數字越小越靠前，用來控制下拉選單中的排列順序。"
    )

    class Meta:
        verbose_name = "職責"
        verbose_name_plural = "職責"
        ordering = ["order", "code"]

    def __str__(self):
        if self.description:
            return f"{self.noun}　{self.description}"
        return self.noun


class WorkAgent(models.Model):
    """
    Agent and its role (i.e. contribution) in relation to the work.
    https://id.loc.gov/ontologies/bibframe.html#Contribution
    """

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="contributions", verbose_name="作品")
    agent = models.ForeignKey(
        "agent.Agent",
        on_delete=models.CASCADE,
        related_name="work_contributions",
        verbose_name="人物/組織",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="work_agents",
        verbose_name="擔任的職責",
        help_text="人物或組織在此作品中的職責，例如「作者」、「繪師」。",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="顯示順序",
        help_text="同一職責有多人時，數字小的排前面。不同職責之間的排序由職責類型本身控制。",
    )

    class Meta:
        unique_together = [("work", "agent", "role")]
        ordering = ["order"]
        verbose_name = "作品創作者"
        verbose_name_plural = "作品創作者"

    def __str__(self):
        return f"{self.work.title} - {self.agent.name} ({self.role.noun})"


class WorkConcept(models.Model):
    """How a specific concept is applied in a work."""

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="work_concepts", verbose_name="作品")
    concept = models.ForeignKey(
        "concept.Concept",
        on_delete=models.CASCADE,
        related_name="work_concepts",
        verbose_name="概念",
    )
    description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="在此作品中的應用方式",
        help_text="說明這個概念在作品中如何呈現，例如「時間旅行：以冬眠技術度過兩千年時光」。可留空。",
    )

    class Meta:
        unique_together = [("work", "concept")]
        verbose_name = "作品相關概念"
        verbose_name_plural = "作品相關概念"

    def __str__(self):
        return f"{self.work.title} ✕ {self.concept.name}"


class Manifestation(models.Model):
    """Physical embodiment of an expression of a work, mapping Works to Publications."""

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="manifestations", verbose_name="作品")
    publication = models.ForeignKey(
        "Publication", on_delete=models.CASCADE, related_name="manifestations", verbose_name="收錄於此出版品"
    )
    name = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="在此出版品中的篇名",
        help_text="作品在這本出版品中使用了不同的篇名時填寫，例如同一篇短篇在不同選集中有不同譯名。作品與出版品名稱相同可留空。",
    )

    class Meta:
        unique_together = [("work", "publication")]
        verbose_name = "收錄紀錄"
        verbose_name_plural = "收錄紀錄"

    def __str__(self):
        return f"{self.publication.title} - {self.work.title}"


class ManifestationAgent(models.Model):
    """
    Agent and its role (i.e. contribution) in relation to the Manifestation,
    such as a translator for a short story in an anthology.
    """

    manifestation = models.ForeignKey(
        Manifestation,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="收錄紀錄",
        help_text="此人物/組織對應的收錄紀錄（作品 × 出版品）。",
    )
    agent = models.ForeignKey(
        "agent.Agent", on_delete=models.CASCADE, related_name="manifestation_contributions", verbose_name="人物/組織"
    )
    display_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="顯示名稱",
        help_text="若人物/組織在此篇使用了特定筆名或譯名時填寫，否則留空。",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="manifestation_agents",
        verbose_name="擔任的職責",
        help_text="通常是譯者，用以紀錄同一選集的作品有多名譯者的狀況。",
    )
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name="顯示順序", help_text="同一職責有多人時，數字小的排前面。"
    )

    class Meta:
        unique_together = [("manifestation", "agent", "role")]
        ordering = ["order"]
        verbose_name = "收錄作品的參與者"
        verbose_name_plural = "收錄作品的參與者"

    def __str__(self):
        name_to_display = self.display_name or self.agent.name
        publication_title = self.manifestation.publication.title
        work_title = self.manifestation.work.title
        return f"[{publication_title}] 收錄之 <{work_title}> - {name_to_display} ({self.role.noun})"


# ============================================================================
# PUBLICATION
# Represents physical or digital releases and their specific contributors.
# ============================================================================

# --- Enums ---


class PublicationMedia(models.TextChoices):
    BOOK = "book", "書籍"
    MAGAZINE = "magazine", "雜誌"
    NEWSPAPER = "newspaper", "報紙"
    WEBSITE = "website", "網站"
    OTHER = "other", "其它"


# --- Models ---


class Series(TimeStampedModel):
    """A collection of publications, like a book series or magazine"""

    title = models.CharField(max_length=300, verbose_name="叢書名稱")
    note = models.TextField(blank=True, verbose_name="備註")

    class Meta:
        ordering = ["title"]
        verbose_name = "叢書"
        verbose_name_plural = "叢書"

    def __str__(self):
        return self.title


class Publication(TimeStampedModel):
    """
    Resource reflecting an individual, material embodiment of a Work.
    https://id.loc.gov/ontologies/bibframe.html#Instance
    """

    publisher = models.ForeignKey(
        "agent.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_publications",
        verbose_name="出版商",
        help_text="負責出版此作品的人物/組織，通常是商業出版社。不確定可留空。",
    )
    title = models.CharField(
        max_length=300, verbose_name="出版品名稱", help_text="書籍填書名，雜誌填期刊名稱，網站填網站名稱。"
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="副標題",
        help_text="例如《第五號屠宰場》的「兒童十字軍」；也能填寫雜誌名稱未包含的期號資訊。可留空。",
    )
    series = models.ForeignKey(
        Series,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="publications",
        verbose_name="所屬叢書/刊物",
        help_text="出版品可隸屬於特定書系、叢書、類書等無序集合，或是期刊、報紙與雜誌等有序集合。",
    )
    series_order = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="叢書/刊物順序",
        help_text="出版品在刊物內的順序，例如雜誌的總期數或是書籍的編號。",
    )
    language = models.CharField(
        max_length=20,
        choices=Language.choices,
        default=Language.ZH_HANT,
        verbose_name="出版語言",
        help_text="此出版品使用的語言，通常是讀者實際閱讀的語言。",
    )
    media = models.CharField(max_length=20, choices=PublicationMedia.choices, verbose_name="出版形式")
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[validate_not_future_year],
        verbose_name="發行年份",
        help_text="此出版品正式發行的年份。不確定可留空。",
    )
    isbn = models.CharField(
        max_length=50,
        blank=True,
        validators=[validate_isbn],
        verbose_name="ISBN",
        help_text="書籍的 ISBN 編號，不含連字號。非書籍或不知道可留空。",
    )
    note = models.CharField(
        max_length=200, blank=True, verbose_name="備註", help_text="補充說明，例如「此版本有刪節」等。可留空。"
    )

    agents = models.ManyToManyField(
        "agent.Agent",
        through="PublicationAgent",
        related_name="publications",
        verbose_name="人物/組織",
        blank=True,
    )

    class Meta:
        ordering = ["year", "title"]
        verbose_name = "出版品"
        verbose_name_plural = "出版品"

    def __str__(self):
        return f"{self.title} ({self.year})"

    def clean(self):
        super().clean()
        if self.series_order is not None and self.series_id is None:
            raise ValidationError({"series_order": "請先填寫叢書/刊物，再登記出版物的順序。"})

    def save(self, *args, **kwargs):
        if self.isbn:
            self.isbn = self.isbn.replace("-", "").replace(" ", "").upper()
        super().save(*args, **kwargs)


class PublicationAgent(models.Model):
    """
    Agent and its role (i.e. contribution) in relation to the publication.
    https://id.loc.gov/ontologies/bibframe.html#Contribution
    """

    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="contributions", verbose_name="出版品"
    )
    agent = models.ForeignKey(
        "agent.Agent",
        on_delete=models.CASCADE,
        related_name="publication_contributions",
        verbose_name="人物/組織",
    )
    display_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="顯示名稱",
        help_text="若此人物/組織在這本出版品中使用了特定筆名或譯名，請填寫；否則留空，系統會自動使用登錄的本名。",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="publication_agents",
        verbose_name="職責",
        help_text="人物/組織在此出版品中的職責，例如「編輯」和「繪師」。",
    )
    order = models.PositiveSmallIntegerField(
        default=0, verbose_name="顯示順序", help_text="同一職責有多人時，數字小的排前面。"
    )

    class Meta:
        unique_together = [("publication", "agent", "role")]
        ordering = ["order"]
        verbose_name = "出版品參與者"
        verbose_name_plural = "出版品參與者"

    def __str__(self):
        name_to_display = self.display_name or self.agent.name
        return f"{self.publication.title} - {name_to_display} ({self.role.noun})"


# ============================================================================
# CATALOGUE
# Represents collections, awards, and reading lists.
# ============================================================================

# --- Enums ---


class CatalogueType(models.TextChoices):
    AWARD = "award", "獎項"
    READING_LIST = "reading_list", "書單"


class AwardStatus(models.TextChoices):
    SELECTED = "selected", "入選"
    WINNER = "winner", "獲獎"


# --- Models ---


class Catalogue(TimeStampedModel):
    """External collections, literary awards, or reading lists."""

    title = models.CharField(
        max_length=300, verbose_name="名稱", help_text="獎項或書單的正式名稱，例如「星雲獎」、「紐約時報書單」。"
    )
    catalogue_type = models.CharField(
        max_length=20,
        choices=CatalogueType.choices,
        verbose_name="類型",
        help_text="「獎項」用於有評選與得獎結果的文學獎；「書單」用於推薦清單、必讀書目等。",
    )
    about = models.TextField(
        blank=True, verbose_name="簡介", help_text="說明這個獎項或書單的背景、評選標準或來源。可留空。"
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[validate_not_future_year],
        verbose_name="舉辦年份",
        help_text="不同年度舉辦的賽事各自獨立，所以要填寫獎項與書單的年份。偶發、不分年度的可留空。",
    )
    agents = models.ManyToManyField(
        "agent.Agent",
        blank=True,
        related_name="curated_catalogues",
        verbose_name="維護者",
        help_text="負責評選或維護此獎項/書單的人物/組織。",
    )

    class Meta:
        verbose_name = "精選"
        verbose_name_plural = "精選"
        ordering = ["title"]

    def __str__(self):
        return self.title


class WorkCatalogue(TimeStampedModel):
    catalogue = models.ForeignKey(
        Catalogue, on_delete=models.CASCADE, related_name="work_catalogues", verbose_name="獎項/書單"
    )
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name="work_catalogues", verbose_name="作品")
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="項目",
        help_text="獎項中的具體獎別，例如「最佳長篇小說」；書單中的分組，例如「必讀」、「推薦」。可留空。",
    )
    status = models.CharField(
        max_length=20,
        choices=AwardStatus.choices,
        default=AwardStatus.SELECTED,
        verbose_name="入選狀態",
        help_text="「入選」表示進入候選名單但未得獎；「獲獎」表示最終得獎。書單類型請維持「入選」即可。",
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="備註",
        help_text="補充說明，例如「共同得獎」、「特別提及」等特殊情況。可留空。",
    )

    class Meta:
        unique_together = [("catalogue", "work", "category")]
        verbose_name = "獎項與書單收錄紀錄"
        verbose_name_plural = "獎項與書單收錄紀錄"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.work.title} in {self.catalogue.title}"

    def clean(self):
        super().clean()
        if (
            self.status == AwardStatus.WINNER
            and self.catalogue_id
            and self.catalogue.catalogue_type != CatalogueType.AWARD
        ):
            raise ValidationError({"status": "只有「獎項」類型的精選才能標記為「獲獎」，書單請維持「入選」。"})
