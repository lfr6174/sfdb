from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    display_name = models.CharField(
        max_length=50, blank=True, verbose_name="顯示名稱", help_text="前端顯示的作者名稱，以避免暴露登入帳號。"
    )


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class SiteSetting(TimeStampedModel):
    key = models.SlugField(
        max_length=100, unique=True, verbose_name="設定鍵值", help_text="程式內部的識別碼，例如 'contact_form_url'"
    )
    value = models.TextField(verbose_name="設定內容", blank=True, help_text="網址或純文字內容")
    description = models.CharField(max_length=200, blank=True, verbose_name="備註說明", help_text="管理員備註用的說明")
    is_active = models.BooleanField(default=True, verbose_name="是否啟用", help_text="停用後前端將無法取得此設定")

    class Meta:
        verbose_name = "網站設定"
        verbose_name_plural = "網站設定"
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} ({self.description or '無備註'})"
