# Generated by Django 4.0.2 on 2022-02-14 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0006_alter_instrument_contact_person"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="orcid_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]