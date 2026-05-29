from django.db import migrations, models


def copy_alt_text_to_serbian(apps, schema_editor):
    ProductImage = apps.get_model("products", "ProductImage")
    for row in ProductImage.objects.exclude(alt_text="").iterator():
        row.alt_text_sr = row.alt_text
        row.save(update_fields=["alt_text_sr"])


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_recommended_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="productimage",
            name="alt_text_sr",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="Alt text (Serbian)",
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="alt_text_en",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="Alt text (English)",
            ),
        ),
        migrations.RunPython(copy_alt_text_to_serbian, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="productimage",
            name="alt_text",
        ),
    ]
