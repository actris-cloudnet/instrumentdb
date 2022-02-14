# Generated by Django 4.0.2 on 2022-02-14 12:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0004_alter_instrument_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=255)),
                ("email_address", models.EmailField(max_length=254)),
                ("orcid_id", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="instrument",
            name="contact_person",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="instruments.person",
            ),
        ),
    ]
