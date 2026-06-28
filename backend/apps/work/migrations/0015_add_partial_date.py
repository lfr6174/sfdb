import datetime

from django.db import migrations, models


def forwards_data(apps, schema_editor):
    """Populate ori_date/pub_date from existing year values."""
    Work = apps.get_model("work", "Work")
    for work in Work.objects.filter(year__isnull=False, ori_date__isnull=True):
        work.ori_date = datetime.date(work.year, 1, 1)
        work.ori_date_precision = "year"
        work.save(update_fields=["ori_date", "ori_date_precision"])

    Publication = apps.get_model("work", "Publication")
    for pub in Publication.objects.filter(year__isnull=False, pub_date__isnull=True):
        pub.pub_date = datetime.date(pub.year, 1, 1)
        pub.pub_date_precision = "year"
        pub.save(update_fields=["pub_date", "pub_date_precision"])


class Migration(migrations.Migration):

    dependencies = [
        ("work", "0014_rename_media_fields"),
    ]

    operations = [
        # --- Work: add ori_date + ori_date_precision ---
        migrations.AddField(
            model_name="work",
            name="ori_date",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="首度發表日期",
                help_text="作品最早公開發表的日期。只知道年份也可以填寫，精確度會自動計算。",
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="ori_date_precision",
            field=models.CharField(
                choices=[("year", "年"), ("month", "月"), ("day", "日")],
                default="year",
                max_length=10,
                verbose_name="日期精確度",
            ),
        ),
        # --- Publication: add pub_date + pub_date_precision ---
        migrations.AddField(
            model_name="publication",
            name="pub_date",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="出版日期",
                help_text="此出版品正式發行的日期。只知道年份也可以填寫，精確度會自動計算。",
            ),
        ),
        migrations.AddField(
            model_name="publication",
            name="pub_date_precision",
            field=models.CharField(
                choices=[("year", "年"), ("month", "月"), ("day", "日")],
                default="year",
                max_length=10,
                verbose_name="日期精確度",
            ),
        ),
        # --- Update year help_text to indicate auto-sync ---
        migrations.AlterField(
            model_name="work",
            name="year",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="首度發表年份",
                help_text="由系統自動同步，請勿手動編輯。",
            ),
        ),
        migrations.AlterField(
            model_name="publication",
            name="year",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="發行年份",
                help_text="由系統自動同步，請勿手動編輯。",
            ),
        ),
        # --- Data migration: backfill from year ---
        migrations.RunPython(forwards_data, migrations.RunPython.noop),
    ]
