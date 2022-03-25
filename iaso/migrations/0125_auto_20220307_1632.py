# Generated by Django 3.1.14 on 2022-03-07 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("iaso", "0124_profile_dhis2_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="dhis2_id",
            field=models.CharField(blank=True, help_text="Dhis2 user ID for SSO Auth", max_length=128, null=True),
        ),
    ]
