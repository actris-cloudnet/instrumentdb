# Generated by Django 4.0.4 on 2022-05-18 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0016_alter_instrument_pid"),
    ]

    operations = [
        migrations.AddField(
            model_name="instrument",
            name="serial_number",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name="AlternateIdentifier",
        ),
    ]