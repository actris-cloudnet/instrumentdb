# Generated by Django 4.2.7 on 2023-11-01 13:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("instruments", "0035_instrument_new_version"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="instrument",
            options={"permissions": [("can_create_pid", "Can create PID")]},
        ),
    ]