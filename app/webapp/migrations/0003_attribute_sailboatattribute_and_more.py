# Generated by Django 5.2.1 on 2025-05-09 18:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0002_designer_make_property_sailboat_sailboatproperty_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attribute",
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
                        help_text="Name of the attribute", max_length=100, unique=True
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Description of what this attribute represents"
                    ),
                ),
                (
                    "input_type",
                    models.CharField(
                        choices=[
                            ("string", "String"),
                            ("float", "Float"),
                            ("options", "Options"),
                        ],
                        help_text="Type of input for this attribute",
                        max_length=20,
                    ),
                ),
                (
                    "options",
                    models.JSONField(
                        blank=True,
                        help_text="List of allowed options for OPTIONS type attributes",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "attribute",
                "verbose_name_plural": "attributes",
            },
        ),
        migrations.CreateModel(
            name="SailboatAttribute",
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
                    "values",
                    models.JSONField(help_text="List of values for this attribute"),
                ),
            ],
            options={
                "verbose_name": "sailboat attribute",
                "verbose_name_plural": "sailboat attributes",
            },
        ),
        migrations.RemoveIndex(
            model_name="sailboat",
            name="webapp_sail_manufac_d776ff_idx",
        ),
        migrations.RemoveIndex(
            model_name="sailboat",
            name="webapp_sail_manufac_54fc92_idx",
        ),
        migrations.AddIndex(
            model_name="attribute",
            index=models.Index(fields=["name"], name="webapp_attr_name_fc0630_idx"),
        ),
        migrations.AddIndex(
            model_name="attribute",
            index=models.Index(
                fields=["input_type"], name="webapp_attr_input_t_22e4e9_idx"
            ),
        ),
        migrations.AddField(
            model_name="sailboatattribute",
            name="attribute",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sailboat_values",
                to="webapp.attribute",
            ),
        ),
        migrations.AddField(
            model_name="sailboatattribute",
            name="sailboat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attribute_values",
                to="webapp.sailboat",
            ),
        ),
        migrations.DeleteModel(
            name="SailboatProperty",
        ),
        migrations.DeleteModel(
            name="Property",
        ),
        migrations.AddIndex(
            model_name="sailboatattribute",
            index=models.Index(
                fields=["sailboat", "attribute"], name="webapp_sail_sailboa_bb558e_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sailboatattribute",
            unique_together={("sailboat", "attribute")},
        ),
    ]
