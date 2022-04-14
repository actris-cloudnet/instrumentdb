# Generated by Django 4.0.2 on 2022-04-14 08:35

import instruments.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0011_alter_organization_ror_id_alter_person_orcid_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="ror_id",
            field=instruments.fields.RorIdField(
                blank=True, max_length=9, null=True, verbose_name="ROR ID"
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="orcid_id",
            field=instruments.fields.OrcidIdField(
                blank=True, max_length=19, null=True, verbose_name="ORCID iD"
            ),
        ),
    ]
