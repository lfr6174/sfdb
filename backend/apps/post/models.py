from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TimeStampedModel


class PostType(models.TextChoices):
    ANNOUNCEMENT = "announcement", "公告"
    ARTICLE = "article", "文章"
    NEWS = "news", "消息"


class Post(TimeStampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="作者",
        related_name="posts",
    )
    post_type = models.CharField(max_length=20, choices=PostType.choices, verbose_name="類型")
    title = models.CharField(max_length=300, verbose_name="標題")
    body = models.TextField(verbose_name="內文", help_text="支援 Markdown。")

    is_pinned = models.BooleanField(default=False, verbose_name="置頂", help_text="僅對公告有效，需手動取消。")
    history = HistoricalRecords()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title}"

    def clean(self):
        if self.is_pinned and self.post_type != PostType.ANNOUNCEMENT:
            raise ValidationError({"is_pinned": "只有「公告」類型可以設定置頂。"})


class Page(TimeStampedModel):
    slug = models.SlugField(max_length=50, unique=True, verbose_name="網址代稱", help_text="例如: about, faq, terms")
    title = models.CharField(max_length=300, verbose_name="標題")
    body = models.TextField(verbose_name="內文", help_text="支援 Markdown。")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "靜態頁面"
        verbose_name_plural = "靜態頁面"

    def __str__(self):
        return f"{self.title} ({self.slug})"
