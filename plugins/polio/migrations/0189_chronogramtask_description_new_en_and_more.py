# Generated by Django 4.2.14 on 2024-08-07 08:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polio", "0188_migrate_chronogramtask_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="chronogramtask",
            name="description_new_en",
            field=models.TextField(blank=True, max_length=300, verbose_name="description_new"),
        ),
        migrations.AddField(
            model_name="chronogramtask",
            name="description_new_fr",
            field=models.TextField(blank=True, max_length=300, verbose_name="description_new"),
        ),
        migrations.AddField(
            model_name="chronogramtemplatetask",
            name="description_new_en",
            field=models.TextField(blank=True, max_length=300, verbose_name="description_new"),
        ),
        migrations.AddField(
            model_name="chronogramtemplatetask",
            name="description_new_fr",
            field=models.TextField(blank=True, max_length=300, verbose_name="description_new"),
        ),
    ]
