from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TimeStampedModel


class Contributor(TimeStampedModel):
    name = models.CharField(max_length=30, unique=True, verbose_name="名稱", help_text="貢獻者名稱，不能留空。")
    is_anonymous = models.BooleanField(default=True, verbose_name="匿名", help_text="啟用時不公開顯示。")
    about = models.TextField(blank=True, verbose_name="簡述", help_text="質性說明身分背景及主要貢獻，供表彰用。")

    history = HistoricalRecords()

    class Meta:
        ordering = ["name"]
        verbose_name = "貢獻者"
        verbose_name_plural = "貢獻者"

    def __str__(self):
        return self.name

    @property
    def commit_count(self):
        return self.commits.count()


class CommitType(models.TextChoices):
    ADD = "add", "新增"
    FIX = "fix", "勘誤"
    UPDATE = "update", "更新"


class CommitScale(models.TextChoices):
    FIELD = "field", "欄"
    ENTRY = "entry", "筆"
    BATCH = "batch", "批"


class Commit(TimeStampedModel):
    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commits",
        verbose_name="貢獻者",
        help_text="留空表示來源不明或已合併自多人。",
    )
    commit_type = models.CharField(
        max_length=10, choices=CommitType.choices, verbose_name="類型", help_text="貢獻的性質。"
    )
    scale = models.CharField(
        max_length=10, choices=CommitScale.choices, verbose_name="規模", help_text="貢獻的範圍大小。"
    )
    title = models.CharField(
        max_length=100, verbose_name="標題", help_text="一句話說明內容，例：新增《瑕疵人型》(2020)。"
    )
    body = models.TextField(blank=True, verbose_name="備註", help_text="詳細說明貢獻內容、取捨、原始資料等。")
    contributed_on = models.DateField(
        null=True, blank=True, verbose_name="貢獻日期", help_text="實際發生日期，可留空。"
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ["-contributed_on", "-created_at"]
        verbose_name = "貢獻紀錄"
        verbose_name_plural = "貢獻紀錄"

    def __str__(self):
        if not self.contributor or self.contributor.is_anonymous:
            return f"{self.commit_type}({self.scale}): {self.title}"
        else:
            return f"{self.commit_type}({self.scale}): {self.title} by {self.contributor.name}"
