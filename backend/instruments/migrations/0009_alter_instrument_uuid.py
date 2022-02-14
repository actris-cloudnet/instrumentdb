# Generated by Django 4.0.2 on 2022-02-14 12:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('instruments', '0008_instrument_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
