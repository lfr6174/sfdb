from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from import_export.formats.base_formats import CSV
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ImportForm

from .models import SiteSetting, User


class RestrictedImportMixin:
    """CSV only, to keep the upload-parser attack surface small."""

    import_formats = [CSV]


MAX_IMPORT_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


class SizeLimitedImportForm(ImportForm):
    """Django/import-export have no built-in cap on uploaded file size; this adds one."""

    def clean_import_file(self):
        import_file = self.cleaned_data["import_file"]
        if import_file.size > MAX_IMPORT_FILE_SIZE:
            raise ValidationError(f"檔案太大(上限 {MAX_IMPORT_FILE_SIZE // (1024 * 1024)}MB)。")
        return import_file


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "display_name", "email", "is_active", "is_staff", "date_joined")


@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    list_display = ("key", "description", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("key", "description", "value")
