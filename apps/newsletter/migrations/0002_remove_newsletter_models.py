from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Subscriber",
        ),
        migrations.DeleteModel(
            name="EmailCampaign",
        ),
    ]
