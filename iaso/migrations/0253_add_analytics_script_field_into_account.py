# Generated by Django 3.2.22 on 2023-12-20 06:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iaso", "0252_remove_analytics_script_field_from_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="analytics_script",
            field=models.TextField(blank=True, null=True),
        ),
    ]
