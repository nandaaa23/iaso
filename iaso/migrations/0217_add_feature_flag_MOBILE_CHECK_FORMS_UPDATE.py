# Generated by Django 3.2.15 on 2023-06-22 16:00

from django.db import migrations


def create_feature_flags(apps, schema_editor):
    FeatureFlag = apps.get_model("iaso", "FeatureFlag")
    FeatureFlag.objects.create(
        code="MOBILE_CHECK_FORMS_UPDATE",
        name="Mobile: Check if the user can update a form.",
    )


def destroy_feature_flags(apps, schema_editor):
    FeatureFlag = apps.get_model("iaso", "FeatureFlag")
    FeatureFlag.objects.filter(code="MOBILE_CHECK_FORMS_UPDATE").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("iaso", "0216_merge_20230614_0839"),
    ]

    operations = [migrations.RunPython(create_feature_flags, destroy_feature_flags)]
