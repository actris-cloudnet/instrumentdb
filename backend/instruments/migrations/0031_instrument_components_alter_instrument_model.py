# Generated by Django 4.1.2 on 2023-01-24 12:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "instruments",
            "0030_alter_campaign_date_range_alter_campaign_location_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="instrument",
            name="components",
            field=models.ManyToManyField(blank=True, to="instruments.instrument"),
        ),
        migrations.AlterField(
            model_name="instrument",
            name="model",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="instruments.model",
            ),
        ),
    ]
