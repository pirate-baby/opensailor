# Generated by Django 5.2.1 on 2025-05-17 04:21

from django.db import migrations


def add_misc_attribute_section(apps, _schema_editor):
    AttributeSection = apps.get_model("webapp", "AttributeSection")
    AttributeSection.objects.create(
        name="Miscellaneous",
        icon="sailing",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0012_attributesection"),
    ]

    operations = [
        migrations.RunPython(add_misc_attribute_section, migrations.RunPython.noop),
    ]
