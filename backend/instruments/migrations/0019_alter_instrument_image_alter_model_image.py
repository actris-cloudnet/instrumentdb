# Generated by Django 4.0.4 on 2022-05-24 12:28

import sorl.thumbnail.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("instruments", "0018_model_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="instrument",
            name="image",
            field=sorl.thumbnail.fields.ImageField(
                blank=True,
                help_text="Photograph of the instrument on site. Leave empty to use default image of the model.",
                null=True,
                upload_to="",
            ),
        ),
        migrations.AlterField(
            model_name="model",
            name="image",
            field=sorl.thumbnail.fields.ImageField(
                blank=True, null=True, upload_to="", verbose_name="Default image"
            ),
        ),
    ]
