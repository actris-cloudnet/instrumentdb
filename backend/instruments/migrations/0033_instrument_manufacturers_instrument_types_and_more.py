# Generated by Django 4.1.7 on 2023-03-10 11:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("instruments", "0032_alter_instrument_components"),
    ]

    operations = [
        migrations.AddField(
            model_name="instrument",
            name="manufacturers",
            field=models.ManyToManyField(
                blank=True,
                help_text="Leavy empty if model is specified.",
                related_name="manufactured_instruments",
                to="instruments.organization",
            ),
        ),
        migrations.AddField(
            model_name="instrument",
            name="types",
            field=models.ManyToManyField(
                blank=True,
                help_text="Leavy empty if model is specified.",
                to="instruments.type",
            ),
        ),
        migrations.AlterField(
            model_name="instrument",
            name="owners",
            field=models.ManyToManyField(
                related_name="owned_instruments", to="instruments.organization"
            ),
        ),
    ]
