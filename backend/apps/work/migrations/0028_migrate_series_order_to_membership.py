from django.db import migrations


def series_order_to_code(series_order):
    """Decimal('7.00') -> '7'; Decimal('100.00') -> '100'; Decimal('12.50') -> '12.5'."""
    if series_order is None:
        return ""
    text = f"{series_order:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def forwards(apps, schema_editor):
    Publication = apps.get_model("work", "Publication")
    SeriesPublication = apps.get_model("work", "SeriesPublication")

    source = Publication.objects.filter(series__isnull=False)
    memberships = [
        SeriesPublication(
            publication_id=pub.pk,
            series_id=pub.series_id,
            code=series_order_to_code(pub.series_order),
        )
        for pub in source.iterator()
    ]
    SeriesPublication.objects.bulk_create(memberships)

    expected, created = source.count(), SeriesPublication.objects.count()
    if expected != created:
        raise RuntimeError(f"叢書資料遷移不完整：預期 {expected} 筆，實際建立 {created} 筆。")


class Migration(migrations.Migration):

    dependencies = [
        ("work", "0027_add_series_publisher_and_membership"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
