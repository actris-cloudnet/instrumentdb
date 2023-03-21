# Generated by Django 4.1.7 on 2023-03-21 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0033_instrument_manufacturers_instrument_types_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="instrument",
            name="image_attribution",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="model",
            name="image_attribution",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
