# Generated by Django 5.2.1 on 2025-05-17 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0011_auto_20250517_0259"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttributeSection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Section name", max_length=100, unique=True
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        help_text="Icon name or identifier", max_length=100
                    ),
                ),
            ],
            options={
                "verbose_name": "attribute section",
                "verbose_name_plural": "attribute sections",
                "indexes": [
                    models.Index(fields=["name"], name="webapp_attr_name_c4fc13_idx")
                ],
            },
        ),
    ]
