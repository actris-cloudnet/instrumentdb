# Generated by Django 4.1 on 2022-11-10 11:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0028_remove_person_full_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pi",
            name="person",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="instruments.person"
            ),
        ),
    ]
