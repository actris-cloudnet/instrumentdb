# Generated by Django 4.2.7 on 2024-02-15 08:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("instruments", "0038_alter_person_user"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Pi",
            new_name="Contact",
        ),
    ]