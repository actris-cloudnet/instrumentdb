# Generated by Django 4.1 on 2022-09-01 13:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("instruments", "0022_location_remove_instrument_commission_date_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="campaign",
            name="exclude_overlapping_campaigns",
        ),
    ]
