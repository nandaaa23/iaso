# Generated by Django 4.2.13 on 2024-06-21 09:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polio", "0178_subactivity_subactivityscope"),
    ]

    operations = [
        migrations.AddField(
            model_name="round",
            name="age_max",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="round",
            name="age_min",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="round",
            name="age_type",
            field=models.TextField(
                blank=True,
                choices=[("YEARS", "years"), ("MONTHS", "months")],
                null=True,
            ),
        ),
    ]
