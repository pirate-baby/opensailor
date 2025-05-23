# Generated by Django 5.2.1 on 2025-05-11 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0003_attribute_sailboatattribute_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attribute",
            name="input_type",
            field=models.CharField(
                choices=[
                    ("string", "String"),
                    ("float", "Float"),
                    ("options", "Options"),
                    ("integer", "Integer"),
                ],
                help_text="Type of input for this attribute",
                max_length=20,
            ),
        ),
    ]
